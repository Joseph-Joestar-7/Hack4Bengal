from flask_wtf import FlaskForm
from flask_wtf.file import FileField, MultipleFileField, FileAllowed, FileRequired
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms import StringField, SelectMultipleField, FloatField, PasswordField, SubmitField, DateField, TimeField, IntegerField, SelectField, TextAreaField
from wtforms.validators import Length, Email, Optional, DataRequired, ValidationError, NumberRange, Regexp
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


class MatchForm(FlaskForm):
    teamName=StringField("Enter Team Name:", validators=[DataRequired()], render_kw={
            "id": "team-name",
            "class": "form-input w-full px-6 py-4 rounded-2xl text-gray-800 dark:text-gray-800 placeholder-gray-800 dark:placeholder-gray-800 focus:outline-none",
            "placeholder": "e.g., Thunder Bolts"
        }
    )
    gameType=SelectField(
        "Select Game Type:",
        choices=[
            ("",     "Choose a game..."),
            ("cricket",   "🏏 Cricket"),
            ("football",  "⚽ Football"),
            ("tennis",    "🎾 Tennis"),
            ("basketball","🏀 Basketball"),
            ("badminton", "🏸 Badminton"),
        ],
        validators=[DataRequired()],
        render_kw={
            "id": "game-type",
            "class": "form-input w-full px-6 py-4 rounded-2xl text-gray-800 dark:text-gray-800 focus:outline-none appearance-none"
        }
    )
    turfName=StringField(
        "Enter Turf Name:",
        validators=[DataRequired()],
        render_kw={
            "id": "turf-name",
            "class": "form-input w-full px-6 py-4 rounded-2xl text-gray-800 dark:text-gray-800 placeholder-gray-800 dark:placeholder-gray-800 focus:outline-none",
            "placeholder": "e.g., Green Valley Sports Complex"
        }
    )
    location=StringField(
        "Enter Location:",
        validators=[DataRequired()],
        render_kw={
            "id": "location",
            "class": "form-input w-full px-6 py-4 rounded-2xl text-gray-800 dark:text-gray-800 placeholder-gray-800 dark:placeholder-gray-800 focus:outline-none",
            "placeholder": "e.g., Howrah"
        }
    )
    date=DateField(
        "Enter Date:",
        validators=[DataRequired()],
        format="%Y-%m-%d",
        render_kw={
            "id": "date",
            "class": "form-input w-full px-6 py-4 rounded-2xl text-gray-800 dark:text-gray-800 focus:outline-none",
        }
    )
    time=TimeField(
        "Enter Time:",
        validators=[DataRequired()],
        format="%H:%M",
        render_kw={
            "id": "time",
            "class": "form-input w-full px-6 py-4 rounded-2xl text-gray-800 dark:text-gray-800 focus:outline-none",
        }
    )
    players=IntegerField(
        "Players:",
        validators=[DataRequired(), NumberRange(min=1, max=25)],
        render_kw={
            "id": "players",
            "min": 1, "max": 50,
            "class": "form-input w-full px-6 py-4 rounded-2xl text-gray-800 dark:text-gray-800 placeholder-gray-800 dark:placeholder-gray-800 focus:outline-none",
            "placeholder": "e.g., 11"
        }
    )
    skill=SelectField(
        "Skill Requirement:",
        choices=[
            ("",     "Choose skill level..."),
            ("Beginner",   "🔰 Beginner"),
            ("Intermediate",  "✨ Intermediate"),
            ("Advanced",    "💯 Advanced")
        ],
        render_kw={
            "id": "skill-requirement",
            "class": "form-input w-full px-6 py-4 rounded-2xl text-gray-800 dark:text-gray-800 focus:outline-none appearance-none"
        }
    )
    submit=SubmitField(
        "🎯 Generate Team Code",
        render_kw={
            "id": "generate-code-btn",
            "class": "px-8 py-4 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-2xl font-semibold hover:shadow-xl hover:scale-105 transition-all duration-300 transform shadow-lg"
        }
    )

class TurfForm(FlaskForm):
    main_image=FileField(
        'Upload Turf Image',
        validators=[FileRequired(message='Please upload a turf image'),
                    FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
                    ]
    )

    additional_images=MultipleFileField(
        'Additional Images',
        validators=[
            FileAllowed(['jpg','jpeg','png','gif'], 'Images only!')
        ]
    )

    turf_name=StringField('Enter turf name', validators=[DataRequired()])
    owner_name=StringField('Enter owner name', validators=[DataRequired()])
    contact_no=StringField('Phone Number', validators=[
        DataRequired(),
        Regexp(
            r'^\+?\d{7,15}$',
            message="Enter a valid phone number (e.g. +919876543210)"
        )
    ])
    email_address=StringField('Enter email address', validators=[DataRequired()])
    address=StringField('Enter complete address', validators=[DataRequired()])
    city=StringField('Enter city', validators=[DataRequired()])
    state=StringField('Enter state', validators=[DataRequired()])
    pincode=IntegerField('Enter pincode', validators=[DataRequired()])
    cricket_price=FloatField('Cricket Hourly Rate')
    football_price=FloatField('Football Hourly Rate')
    tennis_price=FloatField('Tennis Hourly Rate')
    turf_type=SelectField(
        "Skill Requirement:",
        choices=[
            ("",     "Select turf type..."),
            ("Football",   "🔰 Football"),
            ("Cricket",  "✨ Cricket"),
            ("Tennis",    "💯 Tennis"),
            ("Multi-Sport", "MultiSport")
        ]
    )
    capacity=IntegerField("Enter maximum capacity", validators=[DataRequired()])
    opening_time=TimeField(
        "Opening Time:",
        validators=[DataRequired()],
        format="%H:%M")
    
    closing_time=TimeField(
        "Closing Time:",
        validators=[DataRequired()],
        format="%H:%M")
    
    facilities=SelectMultipleField(
        'Select facilies available',
        choices=[
            ('Parking', 'Parking'),
            ('Changing Rooms', 'Changing Rooms'),
            ('First Aid', 'First Aid'),
            ('Floodlights', 'Floodlights'),
            ('Security Guard', 'Security Guard'),
            ('Washrooms', 'Washrooms'),
            ('Equipment Rental', 'Equipment Rental'),
            ('CCTV', 'CCTV'),
            ('Seating Area', 'Seating Area')
        ],
        option_widget=CheckboxInput(),
        widget=ListWidget(prefix_label=False)
    )

    description=TextAreaField('Describe your turf, special features, rule, etc', validators=[DataRequired()])
    submit=SubmitField('Submit')
    