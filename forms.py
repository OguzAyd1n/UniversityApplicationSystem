# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from flask_wtf.file import FileField, FileAllowed
from models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    confirm_password = PasswordField('Şifreyi Onayla', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Kayıt Ol')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Bu kullanıcı adı zaten alınmış. Lütfen başka bir kullanıcı adı seçin.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Bu e-posta adresi zaten kayıtlı. Lütfen başka bir e-posta adresi kullanın.')

class LoginForm(FlaskForm):
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    remember = BooleanField('Beni Hatırla')
    submit = SubmitField('Giriş Yap')

class RequestResetForm(FlaskForm):
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    submit = SubmitField('Şifre Sıfırlama İsteği Gönder')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Bu e-posta adresine sahip bir hesap bulunamadı.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Şifre', validators=[DataRequired()])
    confirm_password = PasswordField('Şifreyi Onayla', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Şifreyi Sıfırla')

class UpdateAccountForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    picture = FileField('Profil Fotoğrafı Güncelle', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Güncelle')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Bu kullanıcı adı zaten alınmış. Lütfen başka bir kullanıcı adı seçin.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Bu e-posta adresi zaten kayıtlı. Lütfen başka bir e-posta adresi kullanın.')

class MessageForm(FlaskForm):
    recipient = StringField('Alıcı E-posta', validators=[DataRequired(), Email()])
    content = TextAreaField('Mesaj', validators=[DataRequired()])
    submit = SubmitField('Gönder')

class ContentForm(FlaskForm):
    title = StringField('Başlık', validators=[DataRequired()])
    content = TextAreaField('İçerik', validators=[DataRequired()])
    submit = SubmitField('Paylaş')

class AdvancedSearchForm(FlaskForm):
    university_name = StringField('Üniversite Adı')
    start_date = StringField('Başlangıç Tarihi')
    end_date = StringField('Bitiş Tarihi')
    application_status = SelectField('Başvuru Durumu', 
                                   choices=[('', 'Tümü'),
                                          ('Beklemede', 'Beklemede'),
                                          ('Kabul Edildi', 'Kabul Edildi'),
                                          ('Reddedildi', 'Reddedildi')])
    submit = SubmitField('Ara')

class OSYMInfoForm(FlaskForm):
    tc_no = StringField('TC Kimlik No', 
                       validators=[DataRequired(), Length(min=11, max=11)],
                       render_kw={"placeholder": "TC Kimlik Numaranız"})
    
    osym_no = StringField('ÖSYM No', 
                         validators=[DataRequired(), Length(min=8, max=20)],
                         render_kw={"placeholder": "ÖSYM Numaranız"})
    
    year = SelectField('Sınav Yılı',
                      choices=[(str(y), str(y)) for y in range(2024, 2019, -1)],
                      validators=[DataRequired()])
    
    score_say = FloatField('Sayısal Puanınız',
                          validators=[Optional()],
                          render_kw={"placeholder": "Örn: 485.25"})
    
    score_ea = FloatField('Eşit Ağırlık Puanınız',
                         validators=[Optional()],
                         render_kw={"placeholder": "Örn: 425.75"})
    
    score_soz = FloatField('Sözel Puanınız',
                          validators=[Optional()],
                          render_kw={"placeholder": "Örn: 410.50"})
    
    score_dil = FloatField('Dil Puanınız',
                          validators=[Optional()],
                          render_kw={"placeholder": "Örn: 445.00"})
    
    rank_say = IntegerField('Sayısal Sıralamanız',
                           validators=[Optional()],
                           render_kw={"placeholder": "Örn: 25000"})
    
    rank_ea = IntegerField('Eşit Ağırlık Sıralamanız',
                          validators=[Optional()],
                          render_kw={"placeholder": "Örn: 35000"})
    
    rank_soz = IntegerField('Sözel Sıralamanız',
                           validators=[Optional()],
                           render_kw={"placeholder": "Örn: 45000"})
    
    rank_dil = IntegerField('Dil Sıralamanız',
                           validators=[Optional()],
                           render_kw={"placeholder": "Örn: 15000"})
    
    submit = SubmitField('ÖSYM Bilgilerimi Kaydet')

    def validate_tc_no(self, tc_no):
        if not tc_no.data.isdigit():
            raise ValidationError('TC Kimlik No sadece rakamlardan oluşmalıdır.')
        
        if len(tc_no.data) != 11:
            raise ValidationError('TC Kimlik No 11 haneli olmalıdır.')

    def validate_osym_no(self, osym_no):
        if not osym_no.data.isdigit():
            raise ValidationError('ÖSYM No sadece rakamlardan oluşmalıdır.')

