#!/usr/bin/env python3
"""Convert Blogger Atom export to Jekyll _posts/ Markdown files."""

import argparse
import os
import re
import html
from datetime import datetime
import xml.etree.ElementTree as ET


def slugify(title):
    title = title.strip().lower()
    title = html.unescape(title)
    title = re.sub(r"[^a-z0-9]+", "-", title)
    title = title.strip("-")
    if not title:
        title = "post"
    return title


def extract_text_from_html(html_content):
    # Minimal HTML stripping for snippet generation
    text = re.sub(r"<script.*?</script>", "", html_content, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", "", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    return text.strip()


def main():
    parser = argparse.ArgumentParser(description="Convert Blogger Atom XML to Jekyll posts")
    parser.add_argument("input_file", help="Path to blog.xml Atom export")
    parser.add_argument("output_dir", default="_posts", help="Output folder for Jekyll posts")
    parser.add_argument("--no-overwrite", action="store_true", help="Skip existing files")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    tree = ET.parse(args.input_file)
    root = tree.getroot()
    ns = {
        'atom': 'http://www.w3.org/2005/Atom',
        'media': 'http://search.yahoo.com/mrss/',
        'thr': 'http://purl.org/syndication/thread/1.0'
    }

    entries = root.findall('atom:entry', ns)
    if not entries:
        print('No entries found in', args.input_file)
        return

    for entry in entries:
        title_elem = entry.find('atom:title', ns)
        content_elem = entry.find('atom:content', ns)
        published_elem = entry.find('atom:published', ns)
        updated_elem = entry.find('atom:updated', ns)

        title = title_elem.text if title_elem is not None and title_elem.text else 'Tanpa Judul'
        slug = slugify(title)

        date_text = (published_elem.text if published_elem is not None and published_elem.text else
                     (updated_elem.text if updated_elem is not None and updated_elem.text else datetime.now().isoformat()))
        try:
            date = datetime.fromisoformat(date_text.replace('Z', '+00:00'))
        except ValueError:
            # Some timezones may use +07:00, etc
            date = datetime.strptime(date_text[:19], '%Y-%m-%dT%H:%M:%S')

        filename = f"{date:%Y-%m-%d}-{slug}.md"
        out_path = os.path.join(args.output_dir, filename)

        if args.no_overwrite and os.path.exists(out_path):
            print('skip', filename)
            continue

        body = ''
        if content_elem is not None and content_elem.text:
            body = content_elem.text
        else:
            body = ''

        # Use HTML as-is, Jekyll supports markdown and HTML in Markdown file
        # Optional: convert to markdown if you have external lib; we keep HTML simple.
        excerpt = extract_text_from_html(body)[:300].strip()
        if excerpt:
            excerpt = excerpt + '...'

        def yaml_quote(value):
            safe = value.replace('"', '\\"').replace('\n', ' ').strip()
            return f'"{safe}"'

        frontmatter = [
            '---',
            f'title: {yaml_quote(title)}',
            f'date: {date:%Y-%m-%d %H:%M:%S %z}',
            'layout: post',
            f'excerpt: {yaml_quote(excerpt)}' if excerpt else 'excerpt: ""',
        ]

        # categories/tags
        categories = [c.attrib.get('term') for c in entry.findall('atom:category', ns) if c.attrib.get('term')]
        if categories:
            unique_categories = sorted(set(categories))
            frontmatter.append('categories:')
            for cat in unique_categories:
                frontmatter.append(f'  - {yaml_quote(cat)}')

        frontmatter.append('---')

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(frontmatter) + '\n\n')
            f.write(body.strip() + '\n')

        print('wrote', out_path)


if __name__ == '__main__':
    main()
