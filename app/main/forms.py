from flask_wtf import FlaskForm
from wtforms import  PasswordField,  SubmitField,StringField, FileField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Enter')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username.data = "admin"   


class UploadForm(FlaskForm):
    file = FileField('Upload File', validators=[DataRequired()])
    submit = SubmitField('Submit')