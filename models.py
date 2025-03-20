# models.py

from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from itsdangerous import URLSafeTimedSerializer as Serializer
from config import Config

db = SQLAlchemy()

class UserOSYMInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tc_no = db.Column(db.String(11), unique=True, nullable=False)
    osym_no = db.Column(db.String(20), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)  # Sınav yılı
    score_say = db.Column(db.Float)  # Sayısal puan
    score_ea = db.Column(db.Float)   # Eşit ağırlık puanı
    score_soz = db.Column(db.Float)  # Sözel puan
    score_dil = db.Column(db.Float)  # Dil puanı
    rank_say = db.Column(db.Integer) # Sayısal sıralama
    rank_ea = db.Column(db.Integer)  # Eşit ağırlık sıralama
    rank_soz = db.Column(db.Integer) # Sözel sıralama
    rank_dil = db.Column(db.Integer) # Dil sıralama
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"UserOSYMInfo(TC: {self.tc_no}, Year: {self.year})"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    has_osym_info = db.Column(db.Boolean, default=False)
    osym_info = db.relationship('UserOSYMInfo', backref='user', uselist=False, lazy=True)
    applications = db.relationship('UserApplication', backref='user', lazy=True)
    favorites = db.relationship('UserFavorite', backref='user', lazy=True)
    notifications = db.relationship('UserNotification', backref='user', lazy=True)
    has_completed_profile = db.Column(db.Boolean, default=False)
    profile = db.relationship('UserProfile', backref='user', uselist=False, lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def get_recommended_departments(self):
        """Kullanıcının ÖSYM puanlarına göre önerilen bölümleri döndürür"""
        if not self.osym_info:
            return []
        
        recommendations = []
        osym = self.osym_info

        # Sayısal puan için öneriler
        if osym.score_say:
            say_depts = Department.query.join(ScoreInfo).filter(
                Department.score_type == 'SAY',
                ScoreInfo.base_score <= osym.score_say
            ).order_by(ScoreInfo.base_score.desc()).limit(5).all()
            recommendations.extend(say_depts)

        # Eşit ağırlık için öneriler
        if osym.score_ea:
            ea_depts = Department.query.join(ScoreInfo).filter(
                Department.score_type == 'EA',
                ScoreInfo.base_score <= osym.score_ea
            ).order_by(ScoreInfo.base_score.desc()).limit(5).all()
            recommendations.extend(ea_depts)

        # Sözel puan için öneriler
        if osym.score_soz:
            soz_depts = Department.query.join(ScoreInfo).filter(
                Department.score_type == 'SÖZ',
                ScoreInfo.base_score <= osym.score_soz
            ).order_by(ScoreInfo.base_score.desc()).limit(5).all()
            recommendations.extend(soz_depts)

        # Dil puanı için öneriler
        if osym.score_dil:
            dil_depts = Department.query.join(ScoreInfo).filter(
                Department.score_type == 'DİL',
                ScoreInfo.base_score <= osym.score_dil
            ).order_by(ScoreInfo.base_score.desc()).limit(5).all()
            recommendations.extend(dil_depts)

        return recommendations

class University(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    yok_id = db.Column(db.String(50), unique=True, nullable=False)  # YÖK ID'si
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Devlet, Vakıf, Özel, KKTC, Yabancı
    website = db.Column(db.String(200))
    departments = db.relationship('Department', backref='university', lazy=True)
    applications = db.relationship('UserApplication', backref='university', lazy=True)

    def __repr__(self):
        return f"University('{self.name}', '{self.location}')"

class UserApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('university.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    application_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Beklemede')
    notes = db.Column(db.Text)

    def __repr__(self):
        return f'<UserApplication {self.user_id} - {self.university_id} - {self.department_id}>'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Message {self.sender_id} to {self.recipient_id}>'

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Content {self.title}>'

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    details = db.Column(db.Text)

    def __repr__(self):
        return f'<Activity {self.user_id} - {self.action}>'

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    yok_id = db.Column(db.String(50), unique=True, nullable=False)  # YÖK ID'si
    name = db.Column(db.String(100), nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('university.id'), nullable=False)
    score_type = db.Column(db.String(20), nullable=False)  # SAY, EA, SÖZ, DİL
    quota = db.Column(db.Integer, nullable=False)
    score_info = db.relationship('ScoreInfo', backref='department', uselist=False, lazy=True)
    applications = db.relationship('UserApplication', backref='department', lazy=True)

    def __repr__(self):
        return f"Department('{self.name}' at '{self.university.name}')"

class ScoreInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    base_score = db.Column(db.Float, nullable=False)  # Taban puan
    ceiling_score = db.Column(db.Float, nullable=False)  # Tavan puan
    year = db.Column(db.Integer, nullable=False)  # Puan bilgilerinin yılı

    def __repr__(self):
        return f"ScoreInfo('{self.department.name}', {self.year})"

class UserFavorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<UserFavorite {self.user_id} - {self.department_id}>'

class UserNotification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<UserNotification {self.user_id} - {self.title}>'

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    country = db.Column(db.String(50))
    birth_date = db.Column(db.Date)
    gender = db.Column(db.String(10))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UserProfile {self.user_id} - {self.first_name} {self.last_name}>'