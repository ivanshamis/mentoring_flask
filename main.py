import json
from http import HTTPStatus

from flask import Flask, Response
from flask_jwt_extended import JWTManager, jwt_required

from extensions import db
from blueprints.docs import docs_bp

from flask_alembic import Alembic
from flask_rest_api import Api


app = Flask(__name__)
app.config["DEBUG"] = True
app.config["JWT_PUBLIC_KEY"] = open("public.pem").read()
app.config["JWT_ALGORITHM"] = "RS256"
app.config["JWT_HEADER_TYPE"] = "Token"
app.config["JWT_IDENTITY_CLAIM"] = "id"
app.config["UPLOAD_FOLDER"] = "uploads"

app.config["DB_HOST"] = "db"
app.config["DB_PORT"] = 5432
app.config["DB_USER"] = "postgres"
app.config["DB_PASSWORD"] = "postgres"
app.config["DB_NAME"] = "postgres"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{app.config['DB_USER']}:{app.config['DB_PASSWORD']}@"
    f"{app.config['DB_HOST']}:{app.config['DB_PORT']}/{app.config['DB_NAME']}"
)
app.config["OPENAPI_VERSION"] = "3.0.2"
db.init_app(app)
jwt = JWTManager(app)
api = Api(app)
api.register_blueprint(docs_bp)

alembic = Alembic()
alembic.init_app(app)
with app.app_context():
    alembic.upgrade()
    # alembic.revision('making changes')


@app.route("/")
@jwt_required()
def index():
    return Response(json.dumps({"data": "Hello world!"}), status=HTTPStatus.OK, mimetype="application/json")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
