from sqlalchemy import Column, Integer
from database import Base

class PurchasedClue(Base):
    __tablename__ = 'users_clues'

    user_id = Column(Integer, primary_key=True)
    task_global_id = Column(Integer, primary_key=True)
    clue_type = Column(Integer, primary_key=True)

