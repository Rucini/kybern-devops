from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired
from app.models import User

class AssignTicketForm(FlaskForm):
    assignee = SelectField('Assign To', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign')

    def __init__(self, *args, **kwargs):
        super(AssignTicketForm, self).__init__(*args, **kwargs)
        self.assignee.choices = [(user.id, user.username) for user in User.query.all()]

class ChangeStatusForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('Open', 'Open'),
        ('Assigned', 'Assigned'),
        ('In Progress', 'In Progress'),
        ('Waiting', 'Waiting'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Status')
