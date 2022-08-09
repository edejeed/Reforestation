import cloudinary
from os import getenv
from flask import Flask
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flaskext.mysql import MySQL
from forestoration.config import Config

load_dotenv()

cloudinary.config(
            cloud_name=getenv("CLOUD_NAME"),
            api_key=getenv("API_KEY"), 
            api_secret=getenv("API_SECRET"),
            secure=getenv("API_SECRET"))

my_sql = MySQL()
bcrypt = Bcrypt()

def create_app(test_config=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    my_sql.init_app(app)
    bcrypt.init_app(app)

    from forestoration.authentication.routes import authentication
    from forestoration.individuals.routes import individuals
    from forestoration.organizations.routes import organization

    app.register_blueprint(authentication)
    app.register_blueprint(individuals)
    app.register_blueprint(organization)

    return app
