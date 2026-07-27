from sqlalchemy import Column, Integer, String, Text

from app.database.database import Base


class ChatHistory(Base):

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(String, index=True)

    role = Column(String)

    content = Column(Text)