from sqlalchemy import Column, BigInteger, Integer, String, DateTime, func

from app.services.database.base import BASE


class User(BASE):
    """Implements base table contains all registered in bot users"""

    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)  # Telegram id
    username = Column(String, default=None)  # Telegram unique @username. Optional.
    firstname = Column(String, default=None)
    lastname = Column(String, default=None)
    language_code = Column(String, default=None)  # Selected language code
    registered_date = Column(DateTime(timezone=True), server_default=func.now())  # On /start press

    def __repr__(self) -> str:
        return f"User: {self.id}, {self.username}, {self.firstname}, " \
               f"{self.lastname}, {self.language_code}, {self.registered_date}"


class Email(BASE):
    __tablename__ = "emails"
    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    user_id = Column(BigInteger)  # User Telegram id
    forum_id = Column(BigInteger, default=None)  # Forum (Telegram chat with emails) id
    mail_server = Column(String)  # Gmail / Yandex / etc.
    mail_address = Column(String, unique=True)  # address@domain
    mail_auth_key = Column(String)  # Generated password. Is encrypted
    last_email_id = Column(Integer, default=0)  # Last sent email_id. Email_id — id from mailbox

    def __repr__(self) -> str:
        return f"Email: {self.id}, {self.user_id}, {self.forum_id}, {self.mail_server} " \
               f"{self.mail_address}, {self.mail_auth_key}, {self.last_email_id}"


class Topic(BASE):
    __tablename__ = "topics"
    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    forum_id = Column(BigInteger)  # Forum (Telegram chat with emails) id
    topic_id = Column(Integer)  # Topic id — unique for forum
    topic_name = Column(String)  # address@domain

    def __repr__(self) -> str:
        return f"Topic: {self.id}, {self.forum_id}, {self.topic_id} " \
               f"{self.topic_name}"
