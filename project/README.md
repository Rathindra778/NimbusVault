# ☁️ NimbusVault — Cloud File Storage System

A full-featured cloud file storage web application built with **Flask**, **SQLite**,
**Bootstrap 5**, and vanilla JavaScript. Features authentication, file management,
dark mode, drag-and-drop upload, an admin panel, and more.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔐 Authentication | Register, Login, Logout with Werkzeug password hashing |
| 📁 File Management | Upload, Download, Delete — per-user isolation |
| 🔍 Search | Filter files by name on the dashboard |
| 🌙 Dark Mode | Persisted via localStorage |
| 🖱️ Drag & Drop | Drag files onto the upload modal |
| 👤 Profile Page | Change password, view stats |
| 🛡️ Admin Panel | View/delete all users and files |
| 📱 Responsive | Mobile-friendly Bootstrap layout |
| ⚡ Flash Messages | Toast notifications for all actions |

---

## 🗂️ Folder Structure

```
project/
├── static/
│   ├── css/
│   │   └── style.css          # Full design system + dark mode
│   └── js/
│       └── main.js            # Dark mode, drag-drop, previews
│
├── templates/
│   ├── base.html              # Navbar, toasts, shared layout
│   ├── login.html             # Login page
│   ├── register.html          # Register page
│   ├── dashboard.html         # File list + upload modal
│   ├── profile.html           # User profile + password change
│   ├── admin.html             # Admin panel
│   └── 404.html               # Error page
│
├── uploads/                   # Uploaded files (auto-created)
├── app.py                     # Main Flask application
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone / Download the project

```bash
cd project
```

### 2. Create and activate a virtual environment

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

The server starts at **http://127.0.0.1:5000**

> The SQLite database (`database.db`) and `uploads/` folder are created
> automatically on first run.

---

## 🚀 First Use

1. Open http://127.0.0.1:5000
2. Click **"Create one"** to register a new account
3. Log in and start uploading files!

### Creating an Admin Account

After registering your first user, open a Python shell:

```bash
python3 - <<'EOF'
from app import app, db, User
with app.app_context():
    u = User.query.filter_by(username='your_username').first()
    u.is_admin = True
    db.session.commit()
    print("Admin granted!")
EOF
```

---

## 📋 Allowed File Types

| Type | Extensions |
|---|---|
| Images | `.jpg` `.jpeg` `.png` `.gif` `.webp` |
| Documents | `.pdf` `.docx` `.txt` |

**Maximum file size:** 16 MB per file

---

## 🔒 Security Notes

- Passwords hashed with `werkzeug.security.generate_password_hash` (PBKDF2-SHA256)
- Filenames sanitised with `werkzeug.utils.secure_filename`
- Files stored with UUID-based names to prevent path traversal
- Session required for all dashboard routes
- Users can only download/delete their own files (admins can access all)
- Change `SECRET_KEY` in `app.py` before deploying to production

---

## 🛠️ Configuration

Edit these values at the top of `app.py`:

```python
app.config['SECRET_KEY']           = 'change-this-in-production'
app.config['MAX_CONTENT_LENGTH']   = 16 * 1024 * 1024   # 16 MB
```

---

## 🖼️ UI Overview

| Screen | Description |
|---|---|
| **Login** | Animated blob background, show/hide password toggle |
| **Register** | Password strength meter, real-time feedback |
| **Dashboard** | Stat cards, searchable file table, drag-and-drop upload modal |
| **Profile** | Avatar, file stats, password change form |
| **Admin Panel** | All users + all files with delete controls |

---

## 📦 Dependencies

```
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Werkzeug==3.0.3
SQLAlchemy==2.0.31
```

Frontend (CDN — no install needed):
- Bootstrap 5.3.2
- Bootstrap Icons 1.11.3
- Google Fonts: Sora, JetBrains Mono

---

## 📄 License

MIT — free to use and modify.
