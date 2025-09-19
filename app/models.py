from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional
from flask_login import UserMixin
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from app import login

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    email: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120), unique=True)
    password: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))  
    type: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20), default='user')  
    score: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, default=0)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)  

    def check_password(self, password):
        return check_password_hash(self.password, password)

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
    

class Ticket(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(140))
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(500))
    status: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20), default='open')  
    priority: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, default=0)
    category_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, sa.ForeignKey('category.id'))
    date_created: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('user.id'))
    category = db.relationship('Category') 
    author = db.relationship('User') 

class Response(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    content: so.Mapped[str] = so.mapped_column(sa.String(500))
    date_created: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    ticket_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('ticket.id'))
    user_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('user.id'), index=True)
    author = db.relationship('User') 
    ticket = db.relationship('Ticket', backref=db.backref('responses', cascade='all, delete-orphan'))

class Category(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(200))