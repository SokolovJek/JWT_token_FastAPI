from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from db.models.users import User
from core.hashing import Hasher


def get_user(username: str, db: Session):
    """
    функция для получения пользователя с БД по его email адресу
    :param username: email c формы
    :param db: объект БД
    :return: user с БД
    """
    user = db.query(User).filter(User.email == username).first()
    return user


def add_hash_to_logout(user: User, db: Session):
    """
    Добавляет хеш к данным пользователя при логине и сохраняет в БД. Для end-point /logout
    :param user: объект пользователя
    :param db: объект БД
    :return: хеш
    """
    hash_to_logout = Hasher.get_hash_to_realize_function_logout(str(user.id))
    user.hash = hash_to_logout
    db.commit()
    return hash_to_logout


def delete_hash_to_logout(user: User, db: Session):
    """
    Удаляет хеш из данных пользователя при логауте. Для end-point /logout
    :param user: объект пользователя
    :param db: объект БД
    :return: dict
    """
    user.hash = ''
    db.commit()
    msg = {'result': True}
    return msg
