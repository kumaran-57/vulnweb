from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------------------
# User Model
# ----------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_encrypted = db.Column(db.Boolean, default=True)

# ----------------------------
# Create Database
# ----------------------------
with app.app_context():
    db.create_all()

# ----------------------------
# Home Page
# ----------------------------
@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('dashboard.html', user=user)

    return render_template('index.html')

# ----------------------------
# Signup
# ----------------------------
@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')
    encrypt = request.form.get('encrypt') == 'true'

    if not username or not password:
        flash('Please fill all fields', 'error')
        return redirect(url_for('index'))

    if User.query.filter_by(username=username).first():
        flash('Username already exists', 'error')
        return redirect(url_for('index'))

    # Store password
    stored_password = generate_password_hash(password) if encrypt else password

    user = User(
        username=username,
        password=stored_password,
        is_encrypted=encrypt
    )

    db.session.add(user)
    db.session.commit()

    flash('Account created successfully', 'success')
    return redirect(url_for('index'))

# ----------------------------
# Normal Login
# ----------------------------
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if not user:
        flash('Invalid username or password', 'error')
        return redirect(url_for('index'))

    # Check password
    if user.is_encrypted:
        valid = check_password_hash(user.password, password)
    else:
        valid = user.password == password

    if valid:
        session['user_id'] = user.id
        flash('Login successful', 'success')
        return redirect(url_for('index'))

    flash('Invalid username or password', 'error')
    return redirect(url_for('index'))

# ----------------------------
# Login Through URL (Demo Only)
# Example:
# /login_url?username=alice&password=1234
# ----------------------------
@app.route('/login_url')
def login_url():
    username = request.args.get('username')
    password = request.args.get('password')

    if not username or not password:
        return '''
        <h3>Usage:</h3>
        <p>/login_url?username=yourname&password=yourpassword</p>
        '''

    user = User.query.filter_by(username=username).first()

    if not user:
        return '''
        <h3>Invalid username</h3>
        <p><a href="/">Back</a></p>
        '''

    # Check password
    if user.is_encrypted:
        valid = check_password_hash(user.password, password)
    else:
        valid = user.password == password

    if valid:
        session['user_id'] = user.id

        return f'''
        <html>
        <head>
            <title>Login Success</title>
            <style>
                body {{
                    font-family: Arial;
                    background: #111827;
                    color: white;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }}
                .box {{
                    background: #1f2937;
                    padding: 40px;
                    border-radius: 20px;
                    text-align: center;
                    width: 350px;
                }}
                a {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 20px;
                    background: #6366f1;
                    color: white;
                    text-decoration: none;
                    border-radius: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="box">
                <h2>Login Successful</h2>
                <p>Welcome, <b>{username}</b></p>
                <a href="/">Go to Dashboard</a>
            </div>
        </body>
        </html>
        '''

    return '''
    <h3>Invalid password</h3>
    <p><a href="/">Back</a></p>
    '''

# ----------------------------
# Logout
# ----------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# ----------------------------
# Run App
# ----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# if __name__ == '__main__': app.run( host='0.0.0.0', port=5000, debug=True, ssl_context='adhoc' )