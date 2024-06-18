from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstName = db.Column(db.String(100), nullable=False)
    secondName = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    otp = db.Column(db.String(6), nullable=True)  # Added the otp column
    
    def __repr__(self):
        return f"<User(id={self.id}, firstName='{self.firstName}', secondName='{self.secondName}', email='{self.email}')>"

    def to_dict(self):
        return {
            'id': self.id,
            'firstName': self.firstName,
            'secondName': self.secondName,
            'email': self.email,
        }
