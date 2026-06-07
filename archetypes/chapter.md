---
title: "{{ replace .Name "-" " " | title }}"
slug: "{{ .Name }}"
novel_slug: "{{ .Section }}"
novel_title: "{{ .Parent.Title }}"
chapter_number: 1
weight: 1
date: {{ .Date }}
draft: true
---

Tulis isi bab novel di sini...
