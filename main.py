import base64
import os
from datetime import datetime
from io import BytesIO

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, RecaptchaField
from itsdangerous import URLSafeTimedSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
import secrets

from config import Config
from forms import AdvancedSearchForm, MessageForm, ContentForm, ResetPasswordForm, RegistrationForm, LoginForm, RequestResetForm, UpdateAccountForm, OSYMInfoForm
from models import db, University, User, Message, Content, Activity, UserApplication, UserOSYMInfo, Department
from utils.osym_scraper import fetch_osym_data, validate_osym_credentials

app = Flask(__name__, template_folder='templates')
app.config.from_object(Config)

# Veritabanı ve diğer eklentilerin başlatılması
db.init_app(app)
mail = Mail(app)
admin = Admin(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Şifre Sıfırlama İsteği',
                  sender='noreply@example.com',
                  recipients=[user.email])
    msg.body = f'''Şifrenizi sıfırlamak için aşağıdaki bağlantıya tıklayın:
{url_for('reset_token', token=token, _external=True)}

Bu e-postayı siz talep etmediyseniz, lütfen dikkate almayın.
'''
    mail.send(msg)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    # Resmi yeniden boyutlandır
    output_size = (150, 150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

@app.route('/')
def home():
    # En çok başvuru alan 5 üniversiteyi getir
    popular_universities = University.query.join(UserApplication)\
        .group_by(University.id)\
        .order_by(db.func.count(UserApplication.id).desc())\
        .limit(5).all()

    # Son 5 duyuruyu getir
    announcements = Content.query.filter_by(user_id=1)\
        .order_by(Content.timestamp.desc())\
        .limit(5).all()

    # Kullanıcıya özel bölüm önerileri
    recommendations = []
    if current_user.is_authenticated and current_user.has_osym_info:
        recommendations = current_user.get_recommended_departments()

    return render_template('home.html', 
                         popular_universities=popular_universities,
                         announcements=announcements,
                         recommendations=recommendations)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Hesabınız başarıyla oluşturuldu! Şimdi giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Kayıt Ol', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Giriş başarısız. Lütfen e-posta ve şifrenizi kontrol edin.', 'danger')
    return render_template('login.html', title='Giriş Yap', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Şifre sıfırlama talimatları e-posta adresinize gönderildi.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Şifre Sıfırlama', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Geçersiz veya süresi dolmuş token.', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user.password_hash = hashed_password
        db.session.commit()
        flash('Şifreniz güncellendi! Şimdi giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Şifre Sıfırlama', form=form)

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            try:
                picture_file = save_picture(form.picture.data)
                current_user.image_file = picture_file
            except Exception as e:
                flash(f'Resim yüklenirken bir hata oluştu: {str(e)}', 'danger')
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Hesabınız başarıyla güncellendi!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + (current_user.image_file or 'default.jpg'))
    return render_template('account.html', title='Hesap', image_file=image_file, form=form)

@app.route('/universities')
def universities():
    universities = University.query.all()
    # Benzersiz şehirleri al ve sırala
    cities = sorted(list(set(u.location for u in universities)))
    return render_template('universities.html', universities=universities, cities=cities)

@app.route('/university/<int:university_id>')
def university_detail(university_id):
    university = University.query.get_or_404(university_id)
    return render_template('university_detail.html', university=university)

@app.route('/department/<int:department_id>')
def department_detail(department_id):
    department = Department.query.get_or_404(department_id)
    return render_template('department_detail.html', department=department)

@app.route('/advanced_search', methods=['GET', 'POST'])
def advanced_search():
    form = AdvancedSearchForm()
    if form.validate_on_submit():
        query = UserApplication.query
        if form.university_name.data:
            query = query.join(University).filter(University.name.contains(form.university_name.data))
        if form.start_date.data:
            query = query.filter(UserApplication.application_date >= form.start_date.data)
        if form.end_date.data:
            query = query.filter(UserApplication.application_date <= form.end_date.data)
        if form.application_status.data:
            query = query.filter(UserApplication.status == form.application_status.data)
        results = query.all()
        return render_template('advanced_search_results.html', results=results)
    return render_template('advanced_search.html', form=form)

@app.route('/user_applications')
@login_required
def user_applications():
    applications = UserApplication.query.filter_by(user_id=current_user.id).all()
    return render_template('user_applications.html', applications=applications)

@app.route('/message_list')
@login_required
def message_list():
    sent_messages = Message.query.filter_by(sender_id=current_user.id).all()
    received_messages = Message.query.filter_by(recipient_id=current_user.id).all()
    return render_template('message_list.html', sent_messages=sent_messages, received_messages=received_messages)

@app.route('/send_message', methods=['GET', 'POST'])
@login_required
def send_message():
    form = MessageForm()
    if form.validate_on_submit():
        recipient = User.query.filter_by(email=form.recipient.data).first()
        if recipient:
            message = Message(
                sender_id=current_user.id,
                recipient_id=recipient.id,
                content=form.content.data
            )
            db.session.add(message)
            db.session.commit()
            flash('Mesajınız gönderildi!', 'success')
            return redirect(url_for('message_list'))
        flash('Alıcı bulunamadı.', 'error')
    return render_template('send_message.html', form=form)

@app.route('/share_content', methods=['GET', 'POST'])
@login_required
def share_content():
    form = ContentForm()
    if form.validate_on_submit():
        content = Content(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id
        )
        db.session.add(content)
        db.session.commit()
        flash('İçeriğiniz paylaşıldı!', 'success')
        return redirect(url_for('content_list'))
    return render_template('share_content.html', form=form)

@app.route('/content_list')
def content_list():
    contents = Content.query.order_by(Content.timestamp.desc()).all()
    return render_template('content_list.html', contents=contents)

@app.route('/content/<int:content_id>')
def content_detail(content_id):
    content = Content.query.get_or_404(content_id)
    return render_template('content_detail.html', content=content)

@app.route('/autocomplete')
def autocomplete():
    term = request.args.get('term', '')
    search_type = request.args.get('type', 'university')
    
    if search_type == 'university':
        results = University.query.filter(University.name.ilike(f'%{term}%')).limit(10).all()
        return jsonify([{'id': u.id, 'value': u.name, 'label': f"{u.name} ({u.location})"} for u in results])
    
    return jsonify([])

@app.route('/osym-info', methods=['GET', 'POST'])
@login_required
def osym_info():
    form = OSYMInfoForm()
    if form.validate_on_submit():
        # Eğer kullanıcının zaten ÖSYM bilgileri varsa güncelle
        if current_user.osym_info:
            osym_info = current_user.osym_info
        else:
            osym_info = UserOSYMInfo(user_id=current_user.id)
            db.session.add(osym_info)

        # Form verilerini kaydet
        osym_info.tc_no = form.tc_no.data
        osym_info.osym_no = form.osym_no.data
        osym_info.year = int(form.year.data)
        osym_info.score_say = form.score_say.data
        osym_info.score_ea = form.score_ea.data
        osym_info.score_soz = form.score_soz.data
        osym_info.score_dil = form.score_dil.data
        osym_info.rank_say = form.rank_say.data
        osym_info.rank_ea = form.rank_ea.data
        osym_info.rank_soz = form.rank_soz.data
        osym_info.rank_dil = form.rank_dil.data

        current_user.has_osym_info = True
        db.session.commit()

        flash('ÖSYM bilgileriniz başarıyla kaydedildi!', 'success')
        return redirect(url_for('osym_info'))

    # Eğer kullanıcının ÖSYM bilgileri varsa formu doldur
    elif request.method == 'GET' and current_user.osym_info:
        form.tc_no.data = current_user.osym_info.tc_no
        form.osym_no.data = current_user.osym_info.osym_no
        form.year.data = str(current_user.osym_info.year)
        form.score_say.data = current_user.osym_info.score_say
        form.score_ea.data = current_user.osym_info.score_ea
        form.score_soz.data = current_user.osym_info.score_soz
        form.score_dil.data = current_user.osym_info.score_dil
        form.rank_say.data = current_user.osym_info.rank_say
        form.rank_ea.data = current_user.osym_info.rank_ea
        form.rank_soz.data = current_user.osym_info.rank_soz
        form.rank_dil.data = current_user.osym_info.rank_dil

    # Önerileri al
    recommendations = current_user.get_recommended_departments() if current_user.has_osym_info else []
    
    return render_template('osym_info.html', title='ÖSYM Bilgileri',
                         form=form, recommendations=recommendations)

@app.route('/fetch-osym-data', methods=['POST'])
@login_required
def fetch_osym_data_endpoint():
    tc_no = request.form.get('tc_no')
    osym_no = request.form.get('osym_no')
    
    if not validate_osym_credentials(tc_no, osym_no):
        return jsonify({
            'success': False,
            'error': 'Geçersiz TC Kimlik No veya ÖSYM şifresi'
        })
    
    try:
        # ÖSYM'den verileri çek
        results = fetch_osym_data(tc_no, osym_no)
        
        # Eğer kullanıcının ÖSYM bilgileri varsa güncelle
        if current_user.osym_info:
            osym_info = current_user.osym_info
        else:
            osym_info = UserOSYMInfo(user_id=current_user.id)
            db.session.add(osym_info)
        
        # Verileri kaydet
        osym_info.tc_no = tc_no
        osym_info.osym_no = osym_no
        osym_info.year = results['year']
        osym_info.score_say = results['score_say']
        osym_info.score_ea = results['score_ea']
        osym_info.score_soz = results['score_soz']
        osym_info.score_dil = results['score_dil']
        osym_info.rank_say = results['rank_say']
        osym_info.rank_ea = results['rank_ea']
        osym_info.rank_soz = results['rank_soz']
        osym_info.rank_dil = results['rank_dil']
        
        current_user.has_osym_info = True
        db.session.commit()
        
        flash('ÖSYM bilgileriniz başarıyla çekildi ve kaydedildi!', 'success')
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/add_application/<int:department_id>', methods=['POST'])
@login_required
def add_application(department_id):
    department = Department.query.get_or_404(department_id)
    
    # Daha önce başvuru yapılmış mı kontrol et
    existing_application = UserApplication.query.filter_by(
        user_id=current_user.id,
        department_id=department.id
    ).first()
    
    if existing_application:
        flash('Bu bölüme daha önce başvuru yapmışsınız.', 'warning')
    else:
        application = UserApplication(
            user_id=current_user.id,
            university_id=department.university.id,
            department_id=department.id
        )
        db.session.add(application)
        db.session.commit()
        flash('Başvurunuz başarıyla kaydedildi.', 'success')
    
    return redirect(url_for('department_detail', department_id=department.id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)