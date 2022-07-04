from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

conn_db = create_engine('sqlite:///RPS_DB.sqlite', echo=True)
base = declarative_base()


class GameDB(base):
    __tablename__ = 'games statistics'
    user_id = Column(Integer, primary_key=True)
    result = Column(String)
    game_time = Column(DateTime)

    def __init__(self, user_id, result, start_credits, game_time):
        self.user_id = user_id
        self.result = result
        self.game_time = game_time
        self.start_credits = start_credits


def create_db():
    base.metadata.create_all(conn_db)
