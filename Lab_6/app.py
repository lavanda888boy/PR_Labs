from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.database import db
from models.scooter import ElectroScooter
    
def create_app():
    app = Flask(__name__)

    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scooter_database.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:test1234@localhost:5432/scooter_db'

    db.init_app(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    import routes
    app.run()
