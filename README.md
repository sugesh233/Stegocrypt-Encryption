# 🛡️ Stegocrypt Encryption

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.1.1-lightgrey)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

> Stegocrypt is a secure web application that combines **RSA encryption** and **image steganography** to hide and retrieve secret messages inside images.

---

## 🚀 Features

- 🔐 **RSA Encryption** (with custom key support)
- 🖼️ **Steganography**: Hide encrypted messages inside images
- 🔍 **Decryption**: Extract and decrypt hidden messages
- 🗂️ **Key Exporting**: Download public/private key pair in JSON format
- ⚙️ **Session Isolation** with Flask
- 🧼 **Automatic Temp File Cleanup** in background thread

---

## 📁 Project Structure

```

Stegocrypt Encryption/
├── app.py                  # Main Flask application
├── main.py                 # Entry point
├── requirements.txt        # All Python dependencies
├── templates/              # HTML templates
├── static/                 # Static assets (CSS, JS, etc.)
├── utils/                  # Crypto and steganography modules
│   ├── crypto.py
│   └── steganography.py
├── .gitignore
└── README.md

````

---

## ⚙️ Getting Started

### 🔧 Prerequisites
- Python 3.10+
- pip

### 🛠️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/sugesh233/stegocrypt-encryption.git
cd stegocrypt-encryption

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt
````

---

## ▶️ Running the App

```bash
python main.py
```

Visit the app at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📦 Technologies Used

| Category       | Technology           |
| -------------- | -------------------- |
| Backend        | Python, Flask        |
| Cryptography   | RSA via PyCryptodome |
| Image Handling | Pillow, NumPy        |
| Frontend       | HTML, Bootstrap      |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ✨ Author

* **Sugesh**
  [GitHub Profile »](https://github.com/sugesh233)

---
