# 🛠️ ctf-dl

**ctf-dl** is a fast and flexible command-line tool for downloading CTF challenges from various platforms. It supports authentication, filtering and custom templates.

> [!WARNING]
> This project is still in development

## 🚀 Quickstart

```bash
ctf-dl https://demo.ctfd.io --token YOUR_TOKEN
```

---

## 🔧 Features

- 🔽 Download **all challenges**: descriptions, files, points, and categories
- 🔁 **Update mode**: only fetch new challenges
- 🧪 **Dry-run mode**: preview output without saving
- 🗂️ Organize challenges with **custom folder structures**
- 🧩 Format output using **custom Jinja2 templates** (Markdown, JSON, etc.)
- 🎯 Apply filters: by category, point range, solved status
- 🔐 Works across platforms via [ctfbridge](https://github.com/bjornmorten/ctfbridge)

---

## 📦 Installation

Install via pip:

```bash
pip install ctf-dl
```

---

## 🧪 CLI Usage

```bash
ctf-dl [OPTIONS] URL
```

**Required argument**:

| Argument | Description |
|----------|-------------|
| `URL`    | Base URL of the CTF platform (e.g., `https://demo.ctfd.io`) |

---

### 📁 Output Options

| Option               | Description                                 | Default        |
|----------------------|---------------------------------------------|----------------|
| `-o`, `--output`     | Output directory to save challenges         | `challenges`   |
| `--template`         | Path to custom challenge template (Jinja2)  | —              |
| `--folder-template`  | Path to folder structure template (Jinja2)  | —              |
| `--zip`              | Compress the output folder into a `.zip`    | —              |

---

### 🔐 Authentication

| Option             | Description             |
|--------------------|-------------------------|
| `-t`, `--token`    | Authentication token    |
| `-u`, `--username` | Username for login      |
| `-p`, `--password` | Password for login      |
| `--cookie`         | Cookie for authentication |

> ⚠️ Provide either a token **or** username/password, not both.

---

### 🔎 Filters

| Option             | Description                                 |
|--------------------|---------------------------------------------|
| `--categories`     | Download only specific categories (e.g. `Web`, `Crypto`) |
| `--min-points`     | Minimum challenge point value               |
| `--max-points`     | Maximum challenge point value               |
| `--solved`         | Download only solved challenges             |
| `--unsolved`       | Download only unsolved challenges           |

---

### ⚙️ Behavior

| Option              | Description                                         | Default |
|---------------------|-----------------------------------------------------|---------|
| `--update`          | Skip already downloaded challenges                 | `False` |
| `--no-attachments`  | Do not download challenge attachments              | `False` |
| `--parallel`        | Number of parallel downloads                       | `30`    |
| `--list-templates`  | List available templates and exit                  | —       |

---

### 🆘 Help

| Option     | Description                 |
|------------|-----------------------------|
| `-h`, `--help` | Show the help message and exit |

---

## 💡 Examples

```bash
# Download all challenges
ctf-dl https://demo.ctfd.io --token YOUR_TOKEN

# Download to a custom directory
ctf-dl https://demo.ctfd.io --token YOUR_TOKEN --output /tmp/ctf

# Only download Web and Crypto challenges
ctf-dl https://demo.ctfd.io --token YOUR_TOKEN --categories Web Crypto

# Update only new challenges
ctf-dl https://demo.ctfd.io --token YOUR_TOKEN --update

# Download and zip output
ctf-dl https://demo.ctfd.io --token YOUR_TOKEN --zip
```

---

## 📁 Default Output Structure

```text
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
