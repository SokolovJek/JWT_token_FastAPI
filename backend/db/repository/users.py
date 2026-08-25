from sqlalchemy.orm import Session

from schemas.users import UserCreate
from db.models.users import User
from core.hashing import Hasher


def create_new_user(user: UserCreate, db: Session):
    """
    Извлекли логику работы с БД из функции create_user(end-point '/user/'),
     для того чтоб в случае чего можно было изменить ORM
    """
    user = User(username=user.username,
                email=user.email,
                hashed_password=Hasher.get_password_hash(user.password),
                hash='',
                is_active=True,
                is_superuser=False
                )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(email: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    return user


def retrieve_user(id_user: int, db: Session):
    """
    Получение конкретного пользователя для (end-point '/user/get/{id_user}/')
    """
    item = db.query(User).filter(User.id == id_user).first()
    return item


def get_user_by_username(username: str, db: Session) -> User:
    """Получение пользователя по username"""
    return db.query(User).filter(User.username == username).first()


def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """Получение всех пользователей с пагинацией"""
    return db.query(User).offset(skip).limit(limit).all()


def update_user(user_id: int, user_data: dict, db: Session) -> User:
    """Обновление данных пользователя"""
    user = retrieve_user(id_user=user_id, db=db)
    if user:
        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
    return user


def delete_user(user_id: int, db: Session) -> bool:
    """Удаление пользователя"""
    user = retrieve_user(id_user=user_id, db=db)
    if user:
        db.delete(user)
        db.commit()
        return True
    return False
