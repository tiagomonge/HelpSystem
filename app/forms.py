from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
import sqlalchemy as sa
from app import db
from app.models import User, Category

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')



class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_confirm = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')
        

class TicketForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=140)])
    category = SelectField("Category", choices=[], coerce=int) 
    description = TextAreaField('Please add your query or problem.', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')


class ResponseForm(FlaskForm):
    content = TextAreaField('Response', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Submit')


class PriorityForm(FlaskForm):
    submit = SubmitField('Set Priority')

class AddCategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=1, max=50)])
    submit_add = SubmitField('Add Category')

    def validate_name(self, field):
        category = db.session.scalar(sa.select(Category).where(
            Category.name == field.data))
        if category is not None:
            raise ValidationError('Please use a different category name.')

class EditCategoryForm(FlaskForm):
    name = StringField('Category Name to Edit', validators=[DataRequired(), Length(min=1, max=50)])
    submit_edit = SubmitField('Update Category')

    def validate_name(self, field):
        category = db.session.scalar(sa.select(Category).where(
            Category.name == field.data))
        if category is not None:
            raise ValidationError('Please use a different category name.')

class DeleteCategoryForm(FlaskForm):
    submit_del = SubmitField('Confirm Delete')

class MarkResolvedForm(FlaskForm):
    submit_resolved = SubmitField('Mark as resolved')