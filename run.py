import os
from dotenv import load_dotenv

# Load .env file at startup
load_dotenv(override=True)

from app import app

if __name__ == "__main__":
    app.run(debug=True)