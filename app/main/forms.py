from flask_wtf import FlaskForm
from wtforms import  SubmitField,StringField, FileField

class UploadForm(FlaskForm):
    file = FileField('Upload File')
    submit = SubmitField('Submit')
    
