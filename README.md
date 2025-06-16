<h1 align="center">
  ctf-dl
</h1>

<h4 align="center">A fast and flexible tool for downloading challenges from all major CTF platforms</h4>                                                                                                 
<p align="center">
  <a href="https://pypi.org/project/ctf-dl/"><img src="https://img.shields.io/pypi/v/ctf-dl" alt="PyPI"></a>
  <img src="https://img.shields.io/github/license/bjornmorten/ctf-dl" alt="License">
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-installation">Install</a> •
  <a href="#-quickstart">Quickstart</a> •
  <a href="#-examples">Examples</a> •
  <a href="#-license">License</a>
</p>


---

## 🔧 Features

* 🔽 Download **all challenges** from a CTF
* 🗂️ Organize challenges with **custom folder structures**
* 🧩 Format output using **custom Jinja2 templates** (Markdown, JSON, etc.)
* 🎯 Apply filters: by category, point range, solved status
* 🔐 Works across all major platforms via [ctfbridge](https://github.com/bjornmorten/ctfbridge)

---

## 📦 Installation

Install via pip:

```bash
pip install ctf-dl
```

---

## 🚀 Quickstart

```bash
ctf-dl https://demo.ctfd.io --token YOUR_TOKEN
```

## 💡 Examples

```bash
# Download all challenges
ctf-dl https://demo.ctfd.io --token YOUR_TOKEN

# Download to a custom directory
ctf-dl https://demo.ctfd.io --token YOUR_TOKEN --output /tmp/ctf

# Use JSON preset format
ctf-dl https://demo.ctfd.io --token YOUR_TOKEN --output-format json

# Only download Web and Crypto challenges
ctf-dl https://demo.ctfd.io --token YOUR_TOKEN --categories Web Crypto

# Update only new challenges
ctf-dl https://demo.ctfd.io --token YOUR_TOKEN --update

# Download and zip output
ctf-dl https://demo.ctfd.io --token YOUR_TOKEN --zip

# List available templates
ctf-dl --list-templates

# Check for updates
ctf-dl --check-update
```

---

## 📁 Default Output Structure

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

---

## 🪪 License

MIT License © 2025 [bjornmorten](https://github.com/bjornmorten)
