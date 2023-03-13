from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import generate_password_hash, check_password_hash

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
    username = payload.get('username', '')
    password = generate_password_hash(payload.get('password', '')).decode("utf8")
    role = payload.get('role','user')
    
    if len(username) > 50:
        return 'username is too long'
    
    user = User(
        username = username, 
        password = password,
        role = role
    )
    db.session.add(user)
    db.session.commit()
    return 'user is created'

@app.route('/login', methods=['POST'])
def login():
    payload = request.json
    username = payload.get('username', '')
    password = payload.get('password', '')
    user = User.query.filter_by(username=username).first()
    
    if user is None:
        return 'User not found'
    
    if check_password_hash(user.password, password) == True:
        return 'Login Success'
    else:
        return 'Incorrect Password'
    
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
    profile= Profile.query.filter_by(id=id).first()
    
    if profile is not None:
        profile.exp = exp
        profile.email = email
        profile.phone = phone
        profile.skills = skills
        db.session.commit()
        return 'Profile updated'
    else:
        return 'Profile not found'
    
@app.route('/change_password/<int:id>', methods=['POST'])
# 1. get user by id
# 2. check if user exist then check pass
# 3. if pass is incorrect then move forward
# 4. if pass is correct then hashed the pass
# 5. then save and commit
def change_password(id):
    payload = request.json
    new_pass = payload.get('new_pass')
    old_pass = payload.get('old_pass')
    user = User.query.filter_by(id= id).first()
    
    if len(new_pass) < 5:
        return 'Password is too short'
    
    if user is None:
        return 'User not found'
    
    if not check_password_hash(user.password, old_pass):
        return 'Old password is incorrect'
    
    hashed_pass = generate_password_hash(new_pass).decode("utf8")
    user.password = hashed_pass
    
    db.session.commit()
    
    return 'password change successfully'
    

if __name__ == 'main':
    app.run(debug=True)
