from datetime import datetime

from flask_serialize import FlaskSerialize
from sqlalchemy import text as sa_text
from sqlalchemy.dialects.postgresql import UUID

from extensions import db

fs_mixin = FlaskSerialize(db)


class Doc(db.Model, fs_mixin):
    __tablename__ = "docs"

    id = db.Column(UUID(as_uuid=True), primary_key=True, server_default=sa_text("uuid_generate_v4()"))
    name = db.Column(db.String(255), index=True, nullable=False)
    extension = db.Column(db.String(100))
    path = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), nullable=False)
    deleted = db.Column(db.Boolean(), default=False)
    created_at = db.Column(db.DateTime(), default=datetime.now())
    thumbnail = db.Column(db.String(1000), nullable=True)

    @property
    def serialize(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "extension": self.extension,
            "path": self.path,
            "user_id": str(self.user_id),
            "deleted": self.deleted,
            "created_at": self.created_at,
            "thumbnail": self.thumbnail,
        }
