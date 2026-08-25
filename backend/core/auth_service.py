# core/auth_service.py
from typing import Optional, Tuple
from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from jose import JWTError

from db.models.users import User
from db.repository.login import get_user, add_hash_to_logout, delete_hash_to_logout
from core.security import create_access_token, create_refresh_token, decode_token
from core.hashing import Hasher
from core.config import settings


class AuthService:
    """Сервис для аутентификации и работы с токенами"""

    @staticmethod
    def login(email: str, password: str, db: Session) -> Tuple[Optional[User], Optional[str], Optional[str]]:
        """
        Аутентификация пользователя и создание токенов

        Args:
            email: Email пользователя
            password: Пароль
            db: Сессия БД

        Returns:
            Tuple[User, str, str]: (пользователь, access_token, refresh_token)
            Если аутентификация не удалась - (None, None, None)
        """
        # 1. Проверяем пользователя
        user = get_user(username=email, db=db)
        if not user:
            return None, None, None

        # 2. Проверяем пароль
        if not Hasher.verify_password(password, user.hashed_password):
            return None, None, None

        # 3. Создаем хеш для сессии
        hash_data = add_hash_to_logout(user=user, db=db)

        # 4. Создаем токены
        access_token = AuthService._create_access_token(email, hash_data)
        refresh_token = AuthService._create_refresh_token(email, hash_data)

        return user, access_token, refresh_token

    @staticmethod
    def refresh_tokens(refresh_token: str, db: Session) -> Tuple[Optional[str], Optional[str]]:
        """
        Обновление токенов по refresh_token

        Args:
            refresh_token: Refresh токен
            db: Сессия БД

        Returns:
            Tuple[str, str]: (новый access_token, новый refresh_token)
            Если обновление не удалось - (None, None)
        """
        try:
            # 1. Декодируем refresh_token
            payload = decode_token(
                token=refresh_token,
                secret_key=settings.SECRET_KEY,
                algorithm=settings.ALGORITHM
            )

            # 2. Проверяем срок действия
            if datetime.utcfromtimestamp(payload.get('exp')) < datetime.utcnow():
                return None, None

            # 3. Извлекаем данные
            email = payload.get('sub')
            hash_to_logout = payload.get('hash_to_logout')

            if not email:
                return None, None

            # 4. Проверяем пользователя
            user = get_user(username=email, db=db)
            if not user:
                return None, None

            # 5. Проверяем, что пользователь не вышел
            if not user.hash:
                return None, None

            # 6. Проверяем, что хеш совпадает
            if hash_to_logout != user.hash:
                return None, None

            # 7. Создаем новые токены
            access_token = AuthService._create_access_token(email, hash_to_logout)
            new_refresh_token = AuthService._create_refresh_token(email, hash_to_logout)

            return access_token, new_refresh_token

        except (JWTError, Exception):
            return None, None

    @staticmethod
    def logout(user: User, db: Session) -> bool:
        """
        Выход пользователя из системы

        Args:
            user: Пользователь
            db: Сессия БД

        Returns:
            bool: Успех операции
        """
        try:
            delete_hash_to_logout(user=user, db=db)
            return True
        except Exception:
            return False

    @staticmethod
    def get_current_user(token: str, db: Session) -> Optional[User]:
        """
        Получение текущего пользователя по токену

        Args:
            token: JWT токен
            db: Сессия БД

        Returns:
            User: Пользователь или None
        """
        try:
            # 1. Декодируем токен
            payload = decode_token(
                token=token,
                secret_key=settings.SECRET_KEY,
                algorithm=settings.ALGORITHM
            )

            # 2. Извлекаем данные
            email = payload.get('sub')
            hash_to_logout = payload.get('hash_to_logout')

            if not email:
                return None

            # 3. Получаем пользователя
            user = get_user(username=email, db=db)
            if not user:
                return None

            # 4. Проверяем, что пользователь не вышел
            if not user.hash:
                return None

            # 5. Проверяем, что хеш совпадает
            if hash_to_logout != user.hash:
                return None

            return user

        except (JWTError, Exception):
            return None

    @staticmethod
    def _create_access_token(email: str, hash_data: str) -> str:
        """Создание access_token"""
        access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(
            data={"sub": email, "hash_to_logout": hash_data},
            expires_delta=access_token_expire
        )

    @staticmethod
    def _create_refresh_token(email: str, hash_data: str) -> str:
        """Создание refresh_token"""
        return create_refresh_token(email, hash_data)
