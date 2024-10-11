from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique = True, nullable = False)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship("Recipe", back_populates="user")

    serialize_rules = ("-recipes.user",)


    @property
    def password_hash(self):
        raise AttributeError ("Access is not allowed")
    
    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password)  

    def check_password(self, password):
       return bcrypt.check_password_hash(self._password_hash, password)
    
    def authenticate(self, password):
        return self.check_password(password)

    
    
class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, nullable = False)
    instructions = db.Column(db.String, nullable = False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", back_populates="recipes")

    serialize_rules = ("-user.recipies",)

    @validates('instructions')
    def validate_instructions(self, key,instructions):
        if len(instructions) >= 50:
            return instructions 
        else: 
            raise ValueError("length must be longer than 50")



