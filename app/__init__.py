from flask import Flask
import os



from database.database import create_tables


app = Flask(
    __name__,
    template_folder=os.path.join("..", "templates"),
    static_folder=os.path.join("..", "static")
)

app.secret_key = "ecet_secret_key"


# Create database tables
create_tables()
from app import routes

