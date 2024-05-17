# flake8: noqa

from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.orm import DeclarativeBase, Mapped

from coaster.sqlalchemy import (
    ModelBase,
    relationship,
    backref,
    Query,
    TimestampMixin,
    DynamicMapped,
)

TimestampMixin.__with_timezone__ = True


class Model(ModelBase, DeclarativeBase):
    """Base model."""


db = SQLAlchemy(metadata=Model.metadata, query_class=Query)  # type: ignore[arg-type]
Model.init_flask_sqlalchemy(db)

from .user import *
from .stored_file import *
from .thumbnail import *
from .profile import *
