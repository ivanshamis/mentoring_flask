import os
from datetime import datetime
from http import HTTPStatus
from PIL import Image

from flask import request, current_app as app
from flask.views import MethodView
from flask_rest_api import Blueprint

from api_utils import paginate, get_filters, get_ordering
from extensions import db
from http_utils import ResponseError
from jwt_utils import jwt_required
from models import Doc

docs_bp = Blueprint("docs_bp", __name__)

IMG_EXTENSIONS = [".gif", ".jpg", ".jpeg", ".png"]
DOC_EXTENSIONS = [".doc", ".docx", ".html", ".pdf", ".txt", ".xsl", ".xlsx"]
VIDEO_EXTENSIONS = [".mp4", ".mov", ".wmv", ".flv", ".avi"]

ALLOWED_EXTENSIONS = IMG_EXTENSIONS + DOC_EXTENSIONS + VIDEO_EXTENSIONS


def save_thumbnail(main_path, doc_id, extension):
    thumbnail_path = None
    if extension in IMG_EXTENSIONS:
        square_fit_size = 100
        image = Image.open(main_path)
        image.thumbnail((square_fit_size, square_fit_size))
        thumbnail_path = os.path.join(app.config["UPLOAD_FOLDER"], str(doc_id) + "_thumb" + extension)
        image.save(thumbnail_path)
    return thumbnail_path


@docs_bp.route("/docs/")
class Docs(MethodView):
    table = Doc
    path = "/docs"
    filter_fields = ["extension", "user_id"]
    default_filter = {"deleted": False}
    ordering_fields = ["created_at", "name"]

    @jwt_required()
    def get(self, *args, **kwargs):
        filters = get_filters(self.filter_fields, self.default_filter)
        ordering = get_ordering(self.ordering_fields, self.table)
        results = self.table.query.filter_by(**filters).order_by(*ordering).all()
        return paginate(results, self.path)

    @jwt_required()
    def post(self, user_id):
        file = request.files.get('file')
        if not file:
            raise ResponseError(status=HTTPStatus.BAD_REQUEST, message="Please provide a file")
        filename, extension = os.path.splitext(file.filename)
        extension = extension.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise ResponseError(status=HTTPStatus.BAD_REQUEST, message="The file type is not allowed")

        doc = self.table(
            name=filename,
            extension=extension,
            path="/",  # will setup the path later
            user_id=user_id,
            created_at=datetime.now()
        )
        db.session.add(doc)
        db.session.flush()
        doc.path = os.path.join(app.config["UPLOAD_FOLDER"], str(doc.id) + extension)
        file.save(doc.path)
        doc.thumbnail = save_thumbnail(doc.path, doc.id, extension)
        db.session.commit()

        return {"result": f"Uploaded: {file.filename} -> {doc.path}"}


@docs_bp.route("/docs/<item_id>")
class DocsById(MethodView):
    @jwt_required()
    def get(self, item_id, *args, **kwargs):
        return Doc.query.filter_by(id=item_id).first().serialize

    @jwt_required()
    def delete(self, item_id, user_id, *args, **kwargs):
        doc = Doc.query.get_or_404(item_id)
        if doc.deleted:
            raise ResponseError(status=HTTPStatus.NOT_FOUND, message="File not found")
        if str(doc.user_id) != str(user_id):
            raise ResponseError(status=HTTPStatus.FORBIDDEN, message="User is not owner of the document")
        doc.deleted = True
        db.session.commit()
        return "", HTTPStatus.NO_CONTENT
