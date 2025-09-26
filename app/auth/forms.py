from flask_wtf import FlaskForm
from wtforms import  PasswordField,  SubmitField,StringField, FileField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Enter')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username.data = "admin"   # default username

    
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    repeat_new_password = PasswordField('Repeat New Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ChangeEmailForm(FlaskForm):
    new_email = StringField("New Email", validators=[DataRequired()])
    submit = SubmitField('Submit')