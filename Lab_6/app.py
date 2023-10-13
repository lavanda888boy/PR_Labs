from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.database import db
from models.scooter import ElectroScooter
    
def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scooter_database.db'
    db.init_app(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    import routes
    app.run()
