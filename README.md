# ctf-dl

ctf-dl is a fast and simple command-line tool for downloading CTF challenges, with support for multiple platforms.

> [!WARNING]
> This project is still in development

## Features

- Download **all challenges** (descriptions, attachments, points, categories) from a CTF platform
- Works with multiple CTF platforms (via [ctfbridge](https://github.com/bjornmorten/ctfbridge/))
- Supports **dry-run** mode to preview downloads without saving
- **Update mode** to only pull new challenges without redownloading everything
- **Filters**:
  - By category (e.g., Web, Crypto)
  - By minimum/maximum points
- Customizable **Jinja2 templates** for easy formatting
- Save challenge data into **custom templates** (Markdown, JSON, plain text, etc.)
- Organize challenges into **custom folder structures**

## Installation

```bash
pip install ctf-dl
```

## Usage

To get a list of all options and switches use:

```bash
ctf-dl -h
```

## Examples

Download all challenges:

```bash
ctf-dl --url https://demo.ctfd.io --username admin --password password
```

Download all challenges to `/tmp/ctf`:

```bash
ctf-dl --url https://demo.ctfd.io --token YOUR_TOKEN --output /tmp/ctf
```

Download only Web and Crypto challenges:

```bash
ctf-dl --url https://ctf.example.com --token YOUR_TOKEN --categories Web Crypto
```

Dry-run (simulate without writing files):

```bash
ctf-dl --url https://ctf.example.com --token YOUR_TOKEN --dry-run
```

Update only new challenges:

```bash
ctf-dl --url https://ctf.example.com --token YOUR_TOKEN --update
```

## Default Output Structure

```
challenges/
├── crypto/
│   ├── rsa-beginner/
│   │   ├── README.md
│   │   └── files/
│   │       ├── chal.py
│   │       └── output.txt
├── web/
│   ├── sql-injection/
│   │   ├── README.md
│   │   └── files/
│   │       └── app.py
```

## License

MIT License © 2025 bjornmorten
