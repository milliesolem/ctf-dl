# 📦 Usage Examples

Here are common real-world examples of using `ctf-dl` to fetch and organize CTF challenges from supported platforms.

---

## 🔓 Basic Usage (Token)

```bash
ctf-dl https://demo.ctfd.io --token ABC123
```

---

## 🗂 Custom Output Folder

```bash
ctf-dl https://demo.ctfd.io --token ABC123 --output ~/ctf-2025
```

---

## 🎯 Filter by Category

```bash
ctf-dl https://demo.ctfd.io --token ABC123 --categories Web Crypto
```

---

## 📉 Filter by Points

```bash
ctf-dl https://demo.ctfd.io --token ABC123 --min-points 100 --max-points 300
```

---

## ✅ Only Solved Challenges

```bash
ctf-dl https://demo.ctfd.io --token ABC123 --solved
```

---

## 🚫 Skip Attachments

```bash
ctf-dl https://demo.ctfd.io --token ABC123 --no-attachments
```

---

## 🔁 Update Mode (Skip Existing)

```bash
ctf-dl https://demo.ctfd.io --token ABC123 --update
```

---

## 🗜 Zip Output After Download

```bash
ctf-dl https://demo.ctfd.io --token ABC123 --zip
```

---

## 🧩 Use a Custom Template

```bash
ctf-dl https://demo.ctfd.io --token ABC123 --template json
```

---

## 🔍 List All Available Templates

```bash
ctf-dl --list-templates
```

