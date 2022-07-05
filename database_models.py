from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

conn_db = create_engine('sqlite:///RPS_DB.sqlite', echo=True)
base = declarative_base()


class UsersDB(base):
    __tablename__ = 'users list'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    credits_ = Column(Integer)
    games = relationship("GameDB", backref='users')

    def __init__(self, user_id, credits_):
        self.user_id = user_id
        self.credits_ = credits_


class GameDB(base):
    __tablename__ = 'games statistics'
    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey("users list.user_id"))
    result = Column(String)
    game_time = Column(DateTime(timezone=True))
    credits_before_game = Column(Integer)

    def __init__(self, user, result, credits_before_game):
        self.user = user
        self.result = result
        self.game_time = func.now()
        self.credits_before_game = credits_before_game


def create_db():
    base.metadata.create_all(conn_db)
