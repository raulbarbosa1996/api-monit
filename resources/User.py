from flask import request
from flask_restful import Resource
from Model_MySQL import db, User, UserSchema
import json
users_schema = UserSchema(many=True)
user_schema = UserSchema()

class UserResource(Resource):
    @staticmethod
    def get():
        print("Aqui")
        users = User.query.all()
        print(users)
        data = users_schema.dump(users)
        # = json.dumps(users)

        return {'status': 'success', 'data': data}, 200
    @staticmethod
    def post():
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'}, 400
        # Validate and deserialize input
        response = json.dumps(json_data)
        data = user_schema.loads(response)
        user = User.query.filter_by(first_name=data['first_name']).first()
        if user:
            return {'message': 'User already exists'}, 400
        user = User(
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        db.session.add(user)
        db.session.commit()
        result = user_schema.dump(user)
        return {"status": 'success', 'data': result}, 201