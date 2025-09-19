from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

from app import models  

with app.app_context():
    db.create_all()
    if not models.Category.query.first(): 
        default_categories = ["Human Resources", "Technology", "Financial"]
        db.session.bulk_save_objects([models.Category(name=cat) for cat in default_categories])
        db.session.commit()


from app import routes, errors