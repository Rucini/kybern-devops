from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from flask import current_app

class TicketForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10)])
    category = SelectField('Category', choices=[
        ('Network', 'Network'),
        ('Hardware', 'Hardware'),
        ('Software', 'Software'),
        ('Email', 'Email'),
        ('Server', 'Server'),
        ('Security', 'Security')
    ], validators=[DataRequired()])
    priority = SelectField('Priority', choices=[
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical')
    ], validators=[DataRequired()])
    
    # We delay evaluating ALLOWED_EXTENSIONS to runtime via a property or just statically define it here.
    # To be safe with current_app context, we can just hardcode or use the set from config.
    attachment = FileField('Attachment', validators=[
        FileAllowed(['pdf', 'png', 'jpg', 'jpeg'], 'PDFs and Images only!')
    ])
    
    submit = SubmitField('Submit Ticket')

class CommentForm(FlaskForm):
    body = TextAreaField('Add a comment', validators=[DataRequired(), Length(min=1)])
    submit = SubmitField('Post Comment')
