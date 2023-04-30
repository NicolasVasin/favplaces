import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Place(SqlAlchemyBase):
    __tablename__ = 'places'
    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    notes = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
                                     
