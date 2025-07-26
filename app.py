"""
Sample Flask Web Application for Testing - FIXED VERSION
A simple web app with login, dashboard, and API endpoints
Fixed: hashlib scrypt compatibility issue
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import hashlib
import secrets
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
app.config['DATABASE'] = 'test_app.db'

def custom_password_hash(password):
    """
    Custom password hashing function for compatibility
    Uses PBKDF2 which is more widely supported
    """
    salt = secrets.token_hex(16)
    # Use PBKDF2 with SHA256 - widely supported
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"pbkdf2:sha256:100000${salt}${hash_obj.hex()}"

def custom_check_password(password_hash, password):
    """
    Custom password verification function
    """
    try:
        method, salt, hash_value = password_hash.split('$')
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return hash_obj.hex() == hash_value
    except:
        # Fallback to Werkzeug if the hash format is different
        try:
            return check_password_hash(password_hash, password)
        except:
            return False

def init_db():
    """Initialize the database with sample data"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create sample user if not exists
    sample_users = [
        ('admin', 'admin@example.com', 'admin123'),
        ('testuser', 'test@example.com', 'password123'),
        ('john_doe', 'john@example.com', 'john123')
    ]
    
    for username, email, password in sample_users:
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if not cursor.fetchone():
            try:
                # Try Werkzeug first
                password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            except Exception as e:
                print(f"⚠️  Werkzeug hash failed, using custom hash for {username}: {e}")
                # Fallback to custom hash
                password_hash = custom_password_hash(password)
            
            cursor.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                         (username, email, password_hash))
            print(f"✅ Created user: {username}")
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Home page - redirects to login if not authenticated"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and authentication"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please fill in all fields', 'error')
            return render_template('login.html')
        
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # Try multiple password verification methods
            password_valid = False
            try:
                # Try Werkzeug first
                password_valid = check_password_hash(user[2], password)
            except:
                # Try custom verification
                password_valid = custom_check_password(user[2], password)
            
            if password_valid:
                session['user_id'] = user[0]
                session['username'] = user[1]
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page - requires authentication"""
    if 'user_id' not in session:
        flash('Please log in to access the dashboard', 'error')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    conn.close()
    
    return render_template('dashboard.html', 
                         username=session.get('username'),
                         user_count=user_count)

@app.route('/profile')
def profile():
    """User profile page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('SELECT username, email, created_at FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# API Endpoints for testing
@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}"
    })

@app.route('/api/db/status')
def db_status():
    """Database connectivity check"""
    try:
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'connected',
            'user_count': count,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/users')
def api_users():
    """API endpoint to get users (requires authentication)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email, created_at FROM users')
    users = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'users': [
            {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'created_at': user[3]
            } for user in users
        ]
    })

@app.route('/api/system/info')
def system_info():
    """System information endpoint"""
    import platform
    return jsonify({
        'platform': platform.system(),
        'python_version': platform.python_version(),
        'flask_version': '3.0.0',
        'hostname': platform.node(),
        'timestamp': datetime.now().isoformat()
    })

def create_templates():
    """Create template files"""
    # Ensure templates directory exists
    os.makedirs('templates', exist_ok=True)
    
    templates = {
        'base.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Test Application{% endblock %}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { background-color: #007bff; color: white; padding: 10px 20px; margin: -20px -20px 20px -20px; border-radius: 8px 8px 0 0; }
        .nav { margin-bottom: 20px; }
        .nav a { color: #007bff; text-decoration: none; margin-right: 15px; }
        .nav a:hover { text-decoration: underline; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .btn { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background-color: #0056b3; }
        .alert { padding: 10px; margin-bottom: 15px; border-radius: 4px; }
        .alert-success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .alert-info { background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        .card { border: 1px solid #ddd; border-radius: 4px; padding: 15px; margin-bottom: 15px; }
        .card h3 { margin-top: 0; }
        .status-badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }
        .status-success { background-color: #28a745; color: white; }
        .status-error { background-color: #dc3545; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{% block header %}Test Application{% endblock %}</h1>
            <span class="status-badge status-success">✅ Fixed Version</span>
        </div>
        
        {% if session.user_id %}
        <div class="nav">
            <a href="{{ url_for('dashboard') }}">Dashboard</a>
            <a href="{{ url_for('profile') }}">Profile</a>
            <a href="{{ url_for('logout') }}">Logout</a>
            <span style="float: right;">Welcome, {{ session.username }}!</span>
        </div>
        {% endif %}
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
</body>
</html>''',
        
        'login.html': '''{% extends "base.html" %}
{% block title %}Login - Test Application{% endblock %}
{% block header %}Login{% endblock %}
{% block content %}
<div class="card">
    <h3>Please Login</h3>
    <form method="POST" id="login-form">
        <div class="form-group">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
        </div>
        <div class="form-group">
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
        </div>
        <button type="submit" class="btn" id="login-btn">Login</button>
    </form>
    
    <div style="margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 4px;">
        <h4>✅ Test Accounts (Fixed Version):</h4>
        <p><strong>admin</strong> / admin123</p>
        <p><strong>testuser</strong> / password123</p>
        <p><strong>john_doe</strong> / john123</p>
    </div>
</div>
{% endblock %}''',
        
        'dashboard.html': '''{% extends "base.html" %}
{% block title %}Dashboard - Test Application{% endblock %}
{% block header %}Dashboard{% endblock %}
{% block content %}
<div class="card">
    <h3>Welcome to your Dashboard, {{ username }}!</h3>
    <p>You have successfully logged in to the test application.</p>
    <span class="status-badge status-success">✅ Authentication Working</span>
</div>

<div class="card">
    <h3>System Statistics</h3>
    <p id="user-count"><strong>Total Users:</strong> {{ user_count }}</p>
    <p><strong>Your Role:</strong> User</p>
    <p><strong>Last Login:</strong> Just now</p>
    <p><strong>Status:</strong> <span class="status-badge status-success">Active</span></p>
</div>

<div class="card">
    <h3>Quick Actions</h3>
    <a href="{{ url_for('profile') }}" class="btn">View Profile</a>
    <a href="{{ url_for('logout') }}" class="btn" style="background-color: #dc3545;">Logout</a>
</div>

<div class="card">
    <h3>API Endpoints</h3>
    <p><a href="/api/health" target="_blank">Health Check</a></p>
    <p><a href="/api/db/status" target="_blank">Database Status</a></p>
    <p><a href="/api/system/info" target="_blank">System Info</a></p>
</div>
{% endblock %}''',
        
        'profile.html': '''{% extends "base.html" %}
{% block title %}Profile - Test Application{% endblock %}
{% block header %}User Profile{% endblock %}
{% block content %}
<div class="card">
    <h3>Your Profile Information</h3>
    {% if user %}
    <p><strong>Username:</strong> {{ user[0] }}</p>
    <p><strong>Email:</strong> {{ user[1] }}</p>
    <p><strong>Member Since:</strong> {{ user[2] }}</p>
    <p><strong>Status:</strong> <span class="status-badge status-success">Active</span></p>
    {% endif %}
</div>

<div class="card">
    <h3>Account Actions</h3>
    <a href="{{ url_for('dashboard') }}" class="btn">Back to Dashboard</a>
</div>
{% endblock %}'''
    }
    
    for filename, content in templates.items():
        filepath = os.path.join('templates', filename)
        try:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✅ Created template: {filename}")
        except Exception as e:
            print(f"❌ Failed to create {filename}: {e}")

if __name__ == '__main__':
    print("🔧 Flask Application Setup (Fixed Version)")
    print("=" * 50)
    
    # Create templates
    print("📁 Creating templates...")
    create_templates()
    
    # Initialize database
    print("🗄️  Initializing database...")
    try:
        init_db()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        exit(1)
    
    print("\n🚀 Flask Application Ready!")
    print("=" * 50)
    print("🌐 Server URL: http://localhost:5000")
    print("\n📝 Test Accounts:")
    print("   👑 admin / admin123")
    print("   👤 testuser / password123")
    print("   👤 john_doe / john123")
    print("\n🔗 API Endpoints:")
    print("   ✅ http://localhost:5000/api/health")
    print("   🗄️  http://localhost:5000/api/db/status")
    print("   👥 http://localhost:5000/api/users")
    print("   💻 http://localhost:5000/api/system/info")
    print("\n🐛 Issue Fixed: hashlib.scrypt compatibility")
    print("💡 Using PBKDF2-SHA256 for password hashing")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)