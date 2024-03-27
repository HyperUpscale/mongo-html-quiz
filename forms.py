from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, IntegerField
from wtforms.validators import DataRequired

class QuizForm(FlaskForm):
    quiz_id = StringField('Quiz ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Create Quiz')

class ImageUploadForm(FlaskForm):
    image = FileField('Image', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    score = IntegerField('Score', validators=[DataRequired()])
    submit = SubmitField('Upload Image')

class ResultImageUploadForm(FlaskForm):
    image = FileField('Image', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    score_range = StringField('Score Range', validators=[DataRequired()])
    result_text = StringField('Result Text', validators=[DataRequired()])
    submit = SubmitField('Upload Result Image')