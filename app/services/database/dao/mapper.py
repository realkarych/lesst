from app.dtos import dto
from app.dtos.database import User, UserEmail, Topic


def map_to_db_user(user: dto.User) -> User:
    """
    :param user: DTO
    :return: database user object
    """

    return User(
        id=user.id,
        username=user.username,
        firstname=user.firstname,
        lastname=user.lastname
    )


def map_to_db_user_email(user_email: dto.UserEmail) -> UserEmail:
    return UserEmail(
        id=user_email.id,
        mail_server=user_email.mail_server,
        mail_address=user_email.mail_address,
        mail_auth_key=user_email.mail_auth_key
    )


def map_to_db_topic(topic: dto.Topic) -> Topic:
    return Topic(
        forum_id=topic.forum_id,
        topic_id=topic.topic_id,
        topic_name=topic.topic_name
    )
