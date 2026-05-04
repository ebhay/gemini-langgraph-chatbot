from database import SessionLocal
from models import Conversation

def save_conversation(user_input, bot_response):
    db = SessionLocal()
    convo = Conversation(user_input=user_input, bot_response=bot_response)
    db.add(convo)
    db.commit()
    db.close()

def get_history(limit=5):
    db = SessionLocal()
    convos = db.query(Conversation).order_by(Conversation.id.desc()).limit(limit).all()
    db.close()

    history = ""
    for c in reversed(convos):
        history += f"User: {c.user_input}\nBot: {c.bot_response}\n"

    return history