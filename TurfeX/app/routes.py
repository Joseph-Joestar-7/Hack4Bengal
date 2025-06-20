from app import app, db
from app.models import User
from app.forms import SignInForm, SignUpForm
from flask import render_template, redirect, url_for, session
from functools import wraps

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def login_required_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            print("Please log in to access this page!!!")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form=SignUpForm()
    if form.validate_on_submit():
        with app.app_context():
            user_data=User(username=form.username.data,
                           email=form.email_address.data,
                           password=form.password.data)
            
            db.session.add(user_data)
            db.session.commit()
            session['user_id']=user_data.id
            
        return redirect(url_for('dashboard'))
    
    if form.errors!={}:
        for err_msg in form.errors.values():
            print(f"There was an error with creating a user : {err_msg}")

    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form=SignInForm()
    if form.validate_on_submit():
        attempted_user=User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            session['user_id']=attempted_user.id
            return redirect(url_for('dashboard'))
        
        else:
            print(f"Username and Password do not match !!! Please try again")

    return render_template('signin.html', form=form)

@app.route('/dashboard')
@login_required_user
def dashboard():
    return render_template('dashboard.html')