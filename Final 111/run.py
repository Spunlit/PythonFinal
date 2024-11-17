from flask import Flask

from app import create_app
import os

app = create_app()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
if __name__ == '__main__':
    app.run(debug=True)
