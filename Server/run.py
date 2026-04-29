import os
import sys

# Add the Server directory to sys.path so we can import 'app' module
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5001)