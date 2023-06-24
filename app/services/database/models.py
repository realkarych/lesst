from datetime import datetime

from sqlalchemy import Column, BigInteger, Integer, String, DateTime, func

from app import dtos
from app.services import cryptography

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
        return f"User: {self.id}, {self.username}, {self.firstname} " \
               f"{self.lastname}, {self.language_code}, {self.registered_date}"

    def to_dto(self) -> dtos.user.UserDTO:
        return dtos.user.UserDTO(
            id=int(str(self.id)),
            username=str(self.username),
            firstname=str(self.firstname),
            lastname=str(self.lastname),
            language_code=str(self.language_code),
            registered_time=datetime.fromisoformat(str(self.registered_date))
        )


class Email(BASE):
    __tablename__ = "emails"
    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    user_id = Column(BigInteger)  # User Telegram id
    forum_id = Column(BigInteger)  # Forum (Telegram chat with emails) id
    mail_server = Column(String)  # Gmail / Yandex / etc.
    mail_address = Column(String)  # address@domain
    mail_auth_key = Column(String)  # Generated password. Is encrypted

    def __repr__(self) -> str:
        return f"Email: {self.id}, {self.user_id}, {self.forum_id}, {self.mail_server} " \
               f"{self.mail_address}, {self.mail_auth_key}"

    def to_dto(self) -> dtos.email.EmailDTO:
        return dtos.email.EmailDTO(
            email_db_id=int(str(self.id)),
            user_id=int(str(self.user_id)),
            forum_id=int(str(self.forum_id)),
            mail_server=str(self.mail_server),
            mail_address=str(self.mail_address),
            mail_auth_key=cryptography.decrypt_key(str(self.mail_auth_key))
        )


class Topic(BASE):
    __tablename__ = "topics"
    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    forum_id = Column(BigInteger)  # Forum (Telegram chat with emails) id
    topic_id = Column(Integer)  # Topic id — unique for forum
    topic_name = Column(String)  # address@domain

    def __repr__(self) -> str:
        return f"Topic: {self.id}, {self.forum_id}, {self.topic_id} " \
               f"{self.topic_name}"

    def to_dto(self) -> dtos.topic.TopicDTO:
        return dtos.topic.TopicDTO(
            topic_db_id=int(str(self.id)),
            topic_id=int(str(self.topic_id)),
            topic_name=str(self.topic_name),
            forum_id=int(str(self.forum_id))
        )
