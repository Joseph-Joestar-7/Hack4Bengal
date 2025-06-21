from app import db
from app import bcrypt
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    __tablename__='users'
    id=db.Column(db.Integer(), primary_key=True)
    username=db.Column(db.String(length=30), nullable=False, unique=True)
    email=db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash=db.Column(db.String(length=60), nullable=False)

    createdMatches=db.relationship('Match', back_populates='creator')
    joinedParticipations=db.relationship('MatchParticipant', back_populates='user')
    bookings=db.relationship('Booking', back_populates='user', cascade='all, delete-orphan', lazy='joined')

    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash=bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    

class TurfOwner(db.Model, UserMixin):
    __tablename__='turf_owners'
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(30), nullable=False, unique=True)
    email=db.Column(db.String(50), nullable=False, unique=True)
    password_hash=db.Column(db.String(128), nullable=False)
    
    turfs=db.relationship('Turf', back_populates='owner', cascade='all, delete-orphan')

    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash=bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)




class Match(db.Model):
    __tablename__='matches'
    id=db.Column(db.Integer(), primary_key=True)
    creator_id=db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    teamName=db.Column(db.String(length=50), nullable=False)
    gameType=db.Column(db.String(length=20), nullable=False)
    turfName=db.Column(db.String(length=20), nullable=False)
    location=db.Column(db.String(length=50), nullable=False)
    createdAt=db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)
    scheduledFor=db.Column(db.DateTime(), nullable=False)
    maxPlayers=db.Column(db.Integer(), default=0)
    skill=db.Column(db.String(length=20), nullable=False)
    status=db.Column(db.String(length=20), default='open', nullable=False)

    creator=db.relationship('User', back_populates='createdMatches')
    participants=db.relationship('MatchParticipant', back_populates='match', cascade='all, delete-orphan', lazy='joined')

class MatchParticipant(db.Model):
    __tablename__='match_participants'
    id=db.Column(db.Integer(), primary_key=True)
    matchId=db.Column(db.Integer(), db.ForeignKey('matches.id'), nullable=False)
    userId=db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    joinedAt=db.Column(db.DateTime(), default=datetime.utcnow)
    role=db.Column(db.String(20), default='player')

    match=db.relationship('Match', back_populates='participants')
    user=db.relationship('User', back_populates='joinedParticipations')


class ChatMessage(db.Model):
    __tablename__='chat_message'
    id=db.Column(db.Integer(), primary_key=True)
    match_id=db.Column(db.Integer(), db.ForeignKey('matches.id'), nullable=False, index=True)
    user_id=db.Column(db.Integer(), db.ForeignKey('users.id'),  nullable=False, index=True)
    text=db.Column(db.Text(),nullable=False)
    timestamp=db.Column(db.DateTime(timezone=True), default=datetime.utcnow, index=True)

    user=db.relationship('User',  backref='chat_messages')
    match=db.relationship('Match', backref='chat_messages')

class Turf(db.Model):
    __tablename__='turfs'
    id=db.Column(db.Integer(), primary_key=True)
    owner_id=db.Column(db.Integer(), db.ForeignKey('turf_owners.id'), nullable=False)
    owner_name=db.Column(db.String(40), nullable=False)
    name=db.Column(db.String(80), nullable=False)
    contact_no=db.Column(db.String(15), nullable=False)
    address=db.Column(db.String(200), nullable=False)
    city=db.Column(db.String(50), nullable=False)
    pincode=db.Column(db.String(10), nullable=False)
    cricket_price=db.Column(db.Float(), default=-1, nullable=False)
    football_price=db.Column(db.Float(), default=-1, nullable=False)
    tennis_price=db.Column(db.Float(), default=-1, nullable=False)
    turf_type=db.Column(db.String(20), nullable=False)
    max_capacity=db.Column(db.Integer(), nullable=False)
    opening_time=db.Column(db.DateTime(), nullable=False)
    closing_time=db.Column(db.DateTime(), nullable=False)
    facilities=db.Column(db.Text(), nullable=False)
    description=db.Column(db.Text(), nullable=True)
    status=db.Column(db.String(20), default='pending')

    owner = db.relationship('TurfOwner', back_populates='turfs')
    bookings = db.relationship('Booking', back_populates='turf', cascade='all, delete-orphan')
    photos=db.relationship('TurfPhoto', back_populates='turf', cascade='all, delete-orphan', lazy='joined')

class Booking(db.Model):
    __tablename__='bookings'
    id=db.Column(db.Integer(), primary_key=True)
    turf_id=db.Column(db.Integer(), db.ForeignKey('turfs.id'), nullable=False, index=True)
    user_id=db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False, index=True)
    start_time=db.Column(db.DateTime(), nullable=False)
    end_time=db.Column(db.DateTime(), nullable=False)
    created_at=db.Column(db.DateTime(), nullable=False)

    turf=db.relationship('Turf', back_populates='bookings')
    user=db.relationship('User', back_populates='bookings')
    
class TurfPhoto(db.Model):
    __tablename__='turf_photos' 
    id=db.Column(db.Integer, primary_key=True)
    turf_id=db.Column(db.Integer, db.ForeignKey('turfs.id', ondelete='CASCADE'), nullable=False, index=True)
    filename=db.Column(db.String(128), nullable=False)
    data=db.Column(db.LargeBinary, nullable=False)
    mimetype=db.Column(db.String(64), nullable=False)
    uploaded_at=db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic=db.Column(db.Boolean, default=False, nullable=False)

    turf=db.relationship('Turf', back_populates='photos')