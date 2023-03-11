from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project.db"
db.init_app(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime,  nullable=True)
    

class Profile(db.Model):
    __tablename__ = 'profile'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", backref="user", uselist=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(50), unique=True)
    avatar = db.Column(db.Text, nullable=True)
    exp = db.Column(db.String(2), nullable=True)
    skills = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime,  nullable=True)
    
with app.app_context():
    db.create_all()
    

@app.route('/register', methods=['POST'])
def register():
    payload = request.json
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(payload.get('password').encode(), salt)
    username = payload.get('username', '')
    role = payload.get('role','user')
    if len(username) > 50:
        return 'username is too long'
    
    user = User(
        username = username, 
        password = hashed,
        role = role
    )
    db.session.add(user)
    db.session.commit()
    return 'user is created'
    
@app.route('/add_newprofile', methods=['POST'])
def add_profile():
    payload = request.json
    user_id = payload.get('user_id','')
    first_name = payload.get('firstname','')
    last_name = payload.get('lastname','')
    email = payload.get('email','')
    phone = payload.get('phone','')
    exp = payload.get('exp','')
    skills = payload.get('skills','')
    
    user = Profile(
        user_id = user_id, 
        first_name = first_name,
        last_name = last_name,
        email = email,
        phone = phone,
        exp = exp,
        skills = skills
    )
    
    db.session.add(user)
    db.session.commit()
    return 'profile is created'
    
@app.route('/show_all_profile', methods=['GET'])
def show_all_profile():
    profiles = db.session.execute(db.select(Profile)).scalars()
    print(profiles)
    return 'test'

@app.route('/update_profile/<int:id>', methods=['PUT','PATCH'])
def update_profile(id):
    payload = request.json
    email = payload.get('email','')
    phone = payload.get('phone','')
    exp = payload.get('exp','')
    skills = payload.get('skills','')
    profile = db.session.execute(db.select(Profile).filter_by(id=id)).scalar_one()
    profile.exp = exp
    profile.email = email
    profile.phone = phone
    profile.skills = skills
    db.session.commit()
    return 'profile updated'  

if __name__ == 'main':
    app.run(debug=True)
