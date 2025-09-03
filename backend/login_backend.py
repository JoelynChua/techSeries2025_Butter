import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from flask_cors import CORS
import bcrypt

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")


app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = JWT_SECRET
jwt = JWTManager(app)



