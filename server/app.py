#!/usr/bin/env python3

from flask import request, session, make_response, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        
        username = data.get('username')
        password = data.get('password')

        # Validate that both username and password are present
        if not data.get('username') or not data.get('password'):
            response = {"error": "Username and password are required"}
            return make_response(jsonify(response), 422)

        user = User.query.filter_by(username=data.get('username')).first()
        if not user: 
            user = User(
                username=data.get('username'),
                password_hash=data.get('password'),
                image_url=data.get('image_url', ''),  # Default to empty string if not provided
                bio=data.get('bio', '')  # Default to empty string if not provided
            )

            try:
                db.session.add(user)
                db.session.commit()

                session['user_id'] = user.id

                return make_response(jsonify(user.to_dict()), 201)
            except IntegrityError:
                db.session.rollback()
                return make_response(jsonify({"error": "Username already exists"}), 422)

        else:
            response = {"error": "Username already exists"}
            return make_response(jsonify(response), 422)

                

class CheckSession(Resource):
    def get(self):
        user = session['user_id']
        if not user:
            response = {"message":"Not logged in"}
            return make_response(jsonify(response), 401)
        else:
            user = User.query.filter_by(id = user).first()
            return make_response(user.to_dict(), 200)


class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            response = {"error" : "username and password are requried"}
            return make_response(jsonify(response, 422))
        
        user = User.query.filter_by(username = username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id 
            return make_response(jsonify(user.to_dict()), 200)
        else:
            response = {"message":"incorrect password"}
            return make_response(jsonify(response), 401)

class Logout(Resource):
    def delete(self):
        session.pop("user_id", None)
        response = {}
        return make_response(jsonify(response), 401)

class RecipeIndex(Resource):
    def get(self):
        if not session.get('user_id'):
            return make_response(jsonify({"error":"Unauthorized"}), 401)
        
        recipies = [recipie.to_dict() for recipie in Recipe.query.all()]
        return make_response(jsonify(recipies), 200)
    
    def post(self):
        data = request.get_json()

        title = data.get('title')
        instructions = data.get('instructions')
        minutes_to_complete = data.get("minutes_to_complete")

        if not title or not instructions or not minutes_to_complete:
            return make_response(jsonify({"message" :"Missing requried fields"}), 422)
        
        if len(instructions) <50:
            return make_response(jsonify({"error": "Instructions must be longer than 50 charachters"}), 422)


        user = User.query.filter_by(id = session.get("user_id")).first()
        if user:
            new_recipie = Recipe(
                title = data.get('title'),
                instructions = data.get('instructions'),
                minutes_to_complete = data.get("minutes_to_complete"),
                user_id = user.id
            )
            db.session.add(new_recipie)
            db.session.commit()

            return make_response(new_recipie.to_dict(), 201)
        else:
            return make_response({"message": "Unauthorized"}, 422)



api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)