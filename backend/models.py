from sqlalchemy import Column, Integer, String
from database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_input = Column(String)
    bot_response = Column(String)