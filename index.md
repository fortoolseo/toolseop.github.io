---
layout: default
title: Blogspot Backup Articles
permalink: /
---

# Blogspot Backup Posts

Ini adalah halaman indeks otomatis untuk post yang diimpor dari `blog.xml`.

<ul>
{% for post in site.posts %}
  <li><a href="{{ post.url }}">{{ post.title }}</a> - <small>{{ post.date | date: "%Y-%m-%d" }}</small></li>
{% endfor %}
</ul>
