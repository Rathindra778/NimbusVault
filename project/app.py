"""
NimbusVault — Cloud File Storage System
Uses Python's built-in sqlite3 (no SQLAlchemy needed).
"""

import os, uuid, sqlite3
from datetime import datetime
from flask import (Flask, render_template, request, redirect,
                   url_for, flash, session, send_from_directory, g)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

# ── App Config ──────────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY']        = 'change-this-in-production'
app.config['UPLOAD_FOLDER']     = os.path.join(os.path.dirname(__file__), 'uploads')
# app.config['MAX_CONTENT_LENGTH']= 16 * 1024 * 1024   # 16 MB
app.config['MAX_CONTENT_LENGTH']= 3072 * 1024 * 1024
DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')
# ALLOWED_EXTENSIONS = {'pdf','png','jpg','jpeg','gif','webp','docx','txt'}
ALLOWED_EXTENSIONS = {
    'pdf','png','jpg','jpeg','gif','webp',
    'docx','txt',
    'mp4','mkv','avi','mov'
}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# ── Database helpers ────────────────────────────────────────
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(_):
    db = getattr(g, '_database', None)
    if db: db.close()

def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT UNIQUE NOT NULL,
            email      TEXT UNIQUE NOT NULL,
            password   TEXT NOT NULL,
            is_admin   INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )""")
    db.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            filename    TEXT NOT NULL,
            filepath    TEXT NOT NULL,
            upload_date TEXT DEFAULT (datetime('now')),
            file_size   INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )""")
    db.commit()
    db.close()


# ── Utility helpers ─────────────────────────────────────────
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def human_size(size):
    for unit in ['B','KB','MB','GB']:
        if size < 1024: return f'{size:.1f} {unit}'
        size /= 1024
    return f'{size:.1f} TB'

def file_ext(filename):
    return filename.rsplit('.',1)[-1].lower() if '.' in filename else ''

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

# Expose helpers to templates
app.jinja_env.globals['human_size'] = human_size
app.jinja_env.globals['file_ext']   = file_ext


# ── Auth Routes ─────────────────────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('dashboard') if 'user_id' in session else url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        email    = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        confirm  = request.form.get('confirm_password','')
        db = get_db()
        errors = []
        if not username or len(username) < 3:    errors.append('Username must be at least 3 characters.')
        if not email or '@' not in email:         errors.append('Enter a valid email address.')
        if len(password) < 6:                    errors.append('Password must be at least 6 characters.')
        if password != confirm:                  errors.append('Passwords do not match.')
        if db.execute('SELECT id FROM users WHERE username=?',(username,)).fetchone():
            errors.append('Username already taken.')
        if db.execute('SELECT id FROM users WHERE email=?',(email,)).fetchone():
            errors.append('Email already registered.')
        if errors:
            for e in errors: flash(e,'danger')
            return render_template('register.html', username=username, email=email)
        db.execute('INSERT INTO users (username,email,password) VALUES (?,?,?)',
                   (username, email, generate_password_hash(password)))
        db.commit()
        flash('Account created! Please log in.','success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        identifier = request.form.get('identifier','').strip()
        password   = request.form.get('password','')
        db  = get_db()
        row = (db.execute('SELECT * FROM users WHERE username=?',(identifier,)).fetchone() or
               db.execute('SELECT * FROM users WHERE email=?',(identifier.lower(),)).fetchone())
        if row and check_password_hash(row['password'], password):
            session['user_id']  = row['id']
            session['username'] = row['username']
            session['is_admin'] = bool(row['is_admin'])
            flash(f"Welcome back, {row['username']}!",'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username/email or password.','danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out.','info')
    return redirect(url_for('login'))


# ── Dashboard ───────────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    db    = get_db()
    uid   = session['user_id']
    query = request.args.get('q','').strip()
    if query:
        rows = db.execute("SELECT * FROM files WHERE user_id=? AND filename LIKE ? ORDER BY upload_date DESC",
                          (uid, f'%{query}%')).fetchall()
    else:
        rows = db.execute("SELECT * FROM files WHERE user_id=? ORDER BY upload_date DESC",(uid,)).fetchall()
    all_files   = db.execute("SELECT file_size FROM files WHERE user_id=?",(uid,)).fetchall()
    total_size  = sum(r['file_size'] for r in all_files)
    total_files = len(all_files)
    user = db.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone()
    return render_template('dashboard.html',
        user=user, files=rows, query=query,
        total_size_human=human_size(total_size),
        total_files=total_files)


# ── Upload ──────────────────────────────────────────────────
@app.route('/upload', methods=['POST'])
@login_required
def upload():
    uid = session['user_id']
    if 'file' not in request.files:
        flash('No file selected.','danger')
        return redirect(url_for('dashboard'))
    uploaded = request.files.getlist('file')
    if not uploaded or all(f.filename=='' for f in uploaded):
        flash('No file selected.','danger')
        return redirect(url_for('dashboard'))
    db = get_db()
    count = 0
    for file in uploaded:
        if file.filename == '': continue
        if not allowed_file(file.filename):
            flash(f'"{file.filename}" — file type not allowed.','warning')
            continue
        original = secure_filename(file.filename)
        ext      = original.rsplit('.',1)[1].lower()
        unique   = f'{uuid.uuid4().hex}.{ext}'
        save_path= os.path.join(app.config['UPLOAD_FOLDER'], unique)
        file.save(save_path)
        size = os.path.getsize(save_path)
        db.execute('INSERT INTO files (user_id,filename,filepath,file_size) VALUES (?,?,?,?)',
                   (uid, original, unique, size))
        count += 1
    db.commit()
    if count: flash(f'{count} file(s) uploaded successfully.','success')
    return redirect(url_for('dashboard'))


# ── Download ────────────────────────────────────────────────
@app.route('/download/<int:file_id>')
@login_required
def download(file_id):
    db   = get_db()
    uid  = session['user_id']
    row  = db.execute('SELECT * FROM files WHERE id=?',(file_id,)).fetchone()
    if not row: flash('File not found.','danger'); return redirect(url_for('dashboard'))
    if row['user_id'] != uid and not session.get('is_admin'):
        flash('Access denied.','danger'); return redirect(url_for('dashboard'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], row['filepath'],
                               as_attachment=True, download_name=row['filename'])


# ── Delete ──────────────────────────────────────────────────
@app.route('/delete/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    db  = get_db()
    uid = session['user_id']
    row = db.execute('SELECT * FROM files WHERE id=?',(file_id,)).fetchone()
    if not row: flash('File not found.','danger'); return redirect(url_for('dashboard'))
    if row['user_id'] != uid and not session.get('is_admin'):
        flash('Access denied.','danger'); return redirect(url_for('dashboard'))
    disk = os.path.join(app.config['UPLOAD_FOLDER'], row['filepath'])
    if os.path.exists(disk): os.remove(disk)
    db.execute('DELETE FROM files WHERE id=?',(file_id,))
    db.commit()
    flash(f'"{row["filename"]}" deleted.','success')
    return redirect(url_for('dashboard'))


# ── Profile ─────────────────────────────────────────────────
@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    db  = get_db()
    uid = session['user_id']
    user= db.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
    if request.method == 'POST':
        current = request.form.get('current_password','')
        new_pw  = request.form.get('new_password','')
        confirm = request.form.get('confirm_password','')
        if not check_password_hash(user['password'], current):
            flash('Current password is incorrect.','danger')
        elif len(new_pw) < 6:
            flash('New password must be at least 6 characters.','danger')
        elif new_pw != confirm:
            flash('New passwords do not match.','danger')
        else:
            db.execute('UPDATE users SET password=? WHERE id=?',(generate_password_hash(new_pw), uid))
            db.commit()
            flash('Password updated successfully.','success')
        return redirect(url_for('profile'))
    files = db.execute('SELECT file_size FROM files WHERE user_id=?',(uid,)).fetchall()
    total_size  = sum(r['file_size'] for r in files)
    return render_template('profile.html',
        user=user, total_files=len(files), total_size_human=human_size(total_size))


# ── Admin ────────────────────────────────────────────────────
@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    db    = get_db()
    users = db.execute('SELECT * FROM users ORDER BY id DESC').fetchall()
    files = db.execute('SELECT f.*,u.username as owner FROM files f JOIN users u ON f.user_id=u.id ORDER BY f.upload_date DESC').fetchall()
    total = sum(r['file_size'] for r in files)
    return render_template('admin.html', users=users, files=files, total_size_human=human_size(total))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    db   = get_db()
    user = db.execute('SELECT * FROM users WHERE id=?',(user_id,)).fetchone()
    if not user: flash('User not found.','danger'); return redirect(url_for('admin_panel'))
    if user['is_admin']: flash('Cannot delete an admin.','danger'); return redirect(url_for('admin_panel'))
    files = db.execute('SELECT filepath FROM files WHERE user_id=?',(user_id,)).fetchall()
    for f in files:
        disk = os.path.join(app.config['UPLOAD_FOLDER'], f['filepath'])
        if os.path.exists(disk): os.remove(disk)
    db.execute('DELETE FROM files WHERE user_id=?',(user_id,))
    db.execute('DELETE FROM users WHERE id=?',(user_id,))
    db.commit()
    flash(f'User "{user["username"]}" deleted.','success')
    return redirect(url_for('admin_panel'))


# ── Error handlers ───────────────────────────────────────────
@app.errorhandler(404)
def not_found(_): return render_template('404.html'), 404

@app.errorhandler(413)
def too_large(_):
    flash('File too large. Maximum size is 16 MB.','danger')
    return redirect(url_for('dashboard'))


# ── Entry point ──────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    print('✅  Database ready.')
    app.run(debug=True, port=5000)
