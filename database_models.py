from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

conn_db = create_engine('sqlite:///RPS_DB.sqlite', echo=True)
base = declarative_base()


class GameDB(base):
    __tablename__ = 'games statistics'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    result = Column(String)
    game_time = Column(DateTime(timezone=True))
    start_credits = Column(Integer)

    def __init__(self, user_id, result, start_credits):
        self.user_id = user_id
        self.result = result
        self.game_time = func.now()
        self.start_credits = start_credits


def create_db():
    base.metadata.create_all(conn_db)
