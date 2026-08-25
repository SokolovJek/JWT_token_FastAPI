# core/user_service.py
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from db.models.users import User
from db.repository.users import (
    create_new_user,
    retrieve_user,
    get_user_by_email,
    get_user_by_username,
    update_user as update_user_db,
    delete_user as delete_user_db,
    get_all_users as get_all_users_db
)
from schemas.users import UserCreate, UserUpdate
from core.hashing import Hasher


class UserService:
    """Сервис для работы с пользователями"""

    @staticmethod
    def create_user(user_data: UserCreate, db: Session) -> User:
        """
        Создание нового пользователя

        Args:
            user_data: Данные пользователя
            db: Сессия БД

        Returns:
            User: Созданный пользователь

        Raises:
            HTTPException: Если пользователь с таким email или username уже существует
        """
        # Проверяем, существует ли пользователь с таким email
        existing_user = get_user_by_email(email=user_data.email, db=db)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Пользователь с email '{user_data.email}' уже существует"
            )

        # Проверяем, существует ли пользователь с таким username
        existing_user = get_user_by_username(username=user_data.username, db=db)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Пользователь с именем '{user_data.username}' уже существует"
            )

        # Создаем пользователя
        user = create_new_user(user=user_data, db=db)
        return user

    @staticmethod
    def get_user_by_id(user_id: int, current_user: User, db: Session) -> User:
        """
        Получение пользователя по ID с проверкой прав

        Args:
            user_id: ID пользователя
            current_user: Текущий авторизованный пользователь
            db: Сессия БД

        Returns:
            User: Найденный пользователь

        Raises:
            HTTPException: Если пользователь не найден или нет прав
        """
        user = retrieve_user(id_user=user_id, db=db)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с идентификатором {user_id} не существует'
            )

        # Проверяем права (владелец или администратор)
        if user.id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"У вас нет прав для просмотра пользователя с id {user_id}"
            )

        return user

    @staticmethod
    def get_current_user_info(current_user: User) -> User:
        """
        Получение информации о текущем пользователе

        Args:
            current_user: Текущий авторизованный пользователь

        Returns:
            User: Текущий пользователь
        """
        return current_user

    @staticmethod
    def get_all_users(skip: int, limit: int, current_user: User, db: Session) -> list[User]:
        """
        Получение списка всех пользователей (только для администраторов)
        """
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только администраторы могут просматривать список всех пользователей"
            )

        return get_all_users_db(db=db, skip=skip, limit=limit)

    @staticmethod
    def update_user(
        user_id: int,
        user_data: Dict[str, Any],
        current_user: User,
        db: Session
    ) -> User:
        """
        Обновление данных пользователя (только для владельца или администратора)
        """
        # 1. Проверяем права
        if user_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет прав для обновления этого пользователя"
            )

        # 2. Получаем пользователя
        user = retrieve_user(id_user=user_id, db=db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с id {user_id} не найден"
            )

        # 3. Проверяем, меняется ли email
        if 'email' in user_data and user_data['email'] != user.email:
            existing = get_user_by_email(email=user_data['email'], db=db)
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email '{user_data['email']}' уже используется"
                )

        # 4. Проверяем, меняется ли is_superuser
        if 'is_superuser' in user_data and not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Поле 'is_superuser' не может менять пользователь"
            )

        # 5. Если меняется пароль - хешируем
        if 'password' in user_data:
            user_data['hashed_password'] = Hasher.get_password_hash(user_data.pop('password'))

        # 6. Обновляем пользователя
        updated_user = update_user_db(user_id=user_id, user_data=user_data, db=db)

        return updated_user

    @staticmethod
    def delete_user(user_id: int, current_user: User, db: Session) -> bool:
        """
        Удаление пользователя (только для администраторов)
        """
        # Проверяем права администратора
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только администраторы могут удалять пользователей"
            )

        # Проверяем, существует ли пользователь
        user = retrieve_user(id_user=user_id, db=db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с id {user_id} не найден"
            )

        # Удаляем пользователя
        return delete_user_db(user_id=user_id, db=db)

    @staticmethod
    def check_user_exists(email: str, db: Session) -> bool:
        """
        Проверка существования пользователя по email

        Args:
            email: Email пользователя
            db: Сессия БД

        Returns:
            bool: True если пользователь существует
        """
        return get_user_by_email(email=email, db=db) is not None

    @staticmethod
    def check_username_exists(username: str, db: Session) -> bool:
        """
        Проверка существования пользователя по username

        Args:
            username: Имя пользователя
            db: Сессия БД

        Returns:
            bool: True если пользователь существует
        """
        return get_user_by_username(username=username, db=db) is not None
