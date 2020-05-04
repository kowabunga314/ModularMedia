from flask import Flask, request
from user.models import User
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '<h1>Hello, World!</h1>'

# @app.route('/user/create', methods=['POST'])
# def create_user():
#     data = request.data
#     user_data = User().create(
#         name=data['name'],
#         email=data['email'],
#         password1=data['password1'],
#         password2=data['password2']
#     )
#     return user_data

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 6969)))
