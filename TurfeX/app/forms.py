from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, Email, Optional, DataRequired, ValidationError
from app import app
from app.models import User
class SignUpForm(FlaskForm):
    def validate_username(self, username_to_check):
        with app.app_context():
            user=User.query.filter_by(username=username_to_check.data).first()

            if user:
                raise ValidationError('Username Already Exist !!!')
            
    def validate_email_address(self, email_address_to_check):
        with app.app_context():
            email=User.query.filter_by(email=email_address_to_check.data).first()

            if email:
                raise ValidationError('Email Address already exists !!!')
            

    username=StringField('Username', validators=[DataRequired(), Length(max=100)], render_kw={"placeholder":"Enter Username"})
    email_address=StringField('Email Address', validators=[DataRequired(), Email(), Length(max=50)], render_kw={"placeholder":"Enter your Email Address"})
    password=PasswordField('Password', validators=[DataRequired(), Length(max=8)], render_kw={"placeholder":"Enter your Password"})
    submit=SubmitField('Sign Up')

class SignInForm(FlaskForm):
    username=StringField('Username', validators=[DataRequired(), Length(max=100)], render_kw={"placeholder":"Enter username"})
    password=PasswordField('Password', validators=[DataRequired(), Length(max=8)], render_kw={"placeholder":"Enter your Password"})
    submit=SubmitField('Sign In')