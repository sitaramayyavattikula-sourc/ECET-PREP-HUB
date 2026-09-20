from flask import Flask
import os
from app.config import Config
from database.database import create_tables

app = Flask(
    __name__,
    template_folder=os.path.join("..", "templates"),
    static_folder=os.path.join("..", "static")
)

app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Create database tables & handle migrations
create_tables()

from app import routes

