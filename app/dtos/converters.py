from datetime import datetime

from app.dtos.email import EmailDTO
from app.dtos.topic import TopicDTO
from app.dtos.user import UserDTO
from app.dtos.incoming_email import IncomingEmailMessageDTO
from app.services import cryptography
from app.services.database.models import User, Email, Topic, IncomingEmailMessage


def convert_db_user_to_dto_user(user: User) -> UserDTO:
    return UserDTO(
        id=int(str(user.id)),
        username=str(user.username),
        firstname=str(user.firstname),
        lastname=str(user.lastname),
        language_code=str(user.language_code),
        registered_time=datetime.fromisoformat(str(user.registered_date))
    )


def convert_db_email_to_dto_email(email: Email) -> EmailDTO:
    return EmailDTO(
        email_db_id=int(str(email.id)),
        user_id=int(str(email.user_id)),
        forum_id=int(str(email.forum_id)),
        mail_server=str(email.mail_server),
        mail_address=str(email.mail_address),
        mail_auth_key=cryptography.decrypt_key(str(email.mail_auth_key))
    )


def convert_db_topic_to_dto_topic(topic: Topic) -> TopicDTO:
    return TopicDTO(
        topic_db_id=int(str(topic.id)),
        topic_id=int(str(topic.topic_id)),
        topic_name=str(topic.topic_name),
        forum_id=int(str(topic.forum_id))
    )


def convert_db_incoming_email_message_to_dto(incoming_email: IncomingEmailMessage) -> IncomingEmailMessageDTO:
    return IncomingEmailMessageDTO(
        email_message_db_id=incoming_email.id,
        email_id=incoming_email.email_id,
        incoming_email_id=incoming_email.incoming_email_id,
        destination_topic_id=incoming_email.destination_topic_id
    )
