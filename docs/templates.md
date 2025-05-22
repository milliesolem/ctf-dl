# 🧩 Template System Documentation for `ctf-dl`

This guide explains the templating system in `ctf-dl`, including how to define, extend, and use templates to control the output of downloaded Capture The Flag (CTF) challenges.

---

## 🎯 Overview

The template system is designed to be **modular, extensible, and easy to customize**. It enables users to:

* Format individual challenge outputs (e.g., README, solve scripts)
* Customize folder structures
* Generate global challenge indexes
* Override or extend default templates without modifying the core tool

---

## 📁 Template Types

Templates are grouped into three functional categories:

| Template Type        | Description                                      | CLI Flag            |
| -------------------- | ------------------------------------------------ | ------------------- |
| **Challenge**        | Controls per-challenge files like README, solves | `--template`        |
| **Folder Structure** | Determines folder layout for challenges          | `--folder-template` |
| **Index**            | Renders a challenge overview or summary          | `--index-template`  |

---

## 🧱 Directory Layout

A custom template directory should follow this structure:

```
my-templates/
├── challenge/
│   ├── _components/
│   │   ├── readme.jinja
│   │   └── solve.py.jinja
│   └── variants/
│       ├── minimal.yaml
│       └── writeup.yaml
├── folder_structure/
│   └── default.path.jinja
└── index/
    └── grouped.md.jinja
```

Specify your template root with:

```bash
ctf-dl --template-dir ./my-templates
```

---

## 📄 Challenge Variants

Variants describe which files should be rendered for each challenge, using a YAML config:

```yaml
name: writeup
components:
  - file: README.md
    template: readme.jinja
  - file: solve/solve.py
    template: solve.py.jinja
```

Use with:

```bash
ctf-dl --template writeup --template-dir ./my-templates
```

### 🔁 Extending Variants

You can use `extends:` to inherit from another variant:

```yaml
extends: base
```

* `components` are inherited unless explicitly overridden.

---

## 🧩 Component Templates

Component templates are stored under `challenge/_components/`. Each Jinja file defines the content for a specific output file:

```jinja
# {{ challenge.name }}

**Points:** {{ challenge.value }}
**Category:** {{ challenge.category }}

{{ challenge.description }}
```

### Supported Variables

* `challenge`: Core metadata (name, category, value, etc.)

Use Jinja’s `{% include %}` or `{% extends %}` to reuse logic between templates.

### 🔄 Overriding Built-in Components

User-defined templates can override built-in components seamlessly. The system uses a layered loading approach:

1. If a component (e.g., `readme.jinja`) exists in the user’s template directory, it will be used.
2. If it does not exist, the system will fall back to the built-in component in the tool’s internal templates.

This makes it easy to:

* Fully replace any default template
* Override only selected parts (e.g., just `solve.py.jinja`)
* Extend base templates using Jinja’s `{% extends %}` syntax:

```jinja
{# user-defined writeup.jinja #}
{% extends "readme.jinja" %}

{% block extra %}
## Additional Notes
- Add any writeup-specific notes here.
{% endblock %}
```

Built-in and user-defined templates are resolved using a Jinja2 `ChoiceLoader`, ensuring full compatibility.

---

## 🗂 Folder Structure Templates

Folder templates determine how each challenge's directory is named and organized.

Example (`default.path.jinja`):

```jinja
{{ challenge.category | slugify }}/{{ challenge.name | slugify }}
```

Apply with:

```bash
ctf-dl --folder-template default
```

---

## 🧾 Index Templates

Index templates render an overview (e.g., `index.md`) listing all downloaded challenges.

Example (`grouped.md.jinja`):

```jinja
# Challenge Index

{% set grouped = {} %}
{% for c in challenges %}{% set _ = grouped.setdefault(c.category, []).append(c) %}{% endfor %}

{% for category, items in grouped.items() %}
## {{ category }}
| Name | Points | Solved | Path |
|------|--------|--------|------|
{% for c in items %}
| {{ c.name }} | {{ c.value }} | {{ "✅" if c.solved else "❌" }} | [Link]({{ c.path }}) |
{% endfor %}
{% endfor %}
```

Apply with:

```bash
ctf-dl --index-template grouped
```

---

## ⚙️ Template Resolution

Templates are resolved using a layered strategy:

1. **User-provided templates** (`--template-dir`)
2. **Built-in defaults** (packaged with `ctf-dl`)

The engine uses a Jinja2 `ChoiceLoader`:

* User templates take precedence
* Built-ins serve as fallback
* Includes and extends work seamlessly across both

This ensures that users can override just what they need, while still benefiting from the system's built-in defaults.

---

## 🧰 Developer Tools

### 🚀 Initialize a Template Directory

```bash
ctf-dl init-template ./my-templates
```

Creates a scaffold with sample components, variants, and helpful comments.

### ✅ Validate a Template Directory

```bash
ctf-dl validate-template --template-dir ./my-templates
```

Checks for:

* Valid YAML structure
* Referenced `.jinja` files
* Jinja syntax errors

---

## ✅ Best Practices

* 🧩 Reuse shared blocks in `_components/`
* 🪄 Use `extends:` to avoid repeating boilerplate
* 🧼 Use slugified folder names to avoid filesystem issues
* 🧪 Validate templates before running exports
* 🧠 Override only the templates you want to change
