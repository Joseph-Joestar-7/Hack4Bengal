from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///GameOn.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY']= 'd29ac4d5dce439ea77f1ef13'

db=SQLAlchemy(app)
bcrypt=Bcrypt(app)

from app import routes