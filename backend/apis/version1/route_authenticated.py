from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi import Depends, APIRouter, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi import status, HTTPException
from jose import JWTError
from fastapi.responses import JSONResponse
from datetime import datetime

from db.session import get_db
from core.hashing import Hasher
from schemas.tokens import Token
from db.repository.login import get_user, add_hash_to_logout, delete_hash_to_logout
from core.security import create_access_token, create_refresh_token, decode_token
from core.config import settings
from db.black_list import add_blacklist_token, is_token_blacklisted


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')


@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    функция для аутентификации пользователя и выдачи ему токена
    :param form_data: данные полученные с формы
    :param db: объект БД
    :return: ответ на запрос
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Некорректный логин или пароль',
        )

    hash_to_logout = add_hash_to_logout(user=user, db=db)
    access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, 'hash_to_logout': hash_to_logout}, expires_delta=access_token_expire
    )

    refresh_token = create_refresh_token(user.email, hash_to_logout)
    return {'access_token': access_token,
            'token_type': 'bearer',
            'refresh_token': refresh_token
            }


@router.post('/logout')
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user_from_token(token, db)
    msg = delete_hash_to_logout(user=user, db=db)
    return JSONResponse(msg)


@router.post('/refresh_jwt')
async def refresh(request: Request, db: Session = Depends(get_db)):
    """
    обновление refresh токена
    """
    try:
        form = await request.json()
        token = form.get('refresh_token')

        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Refresh token не предоставлен'
            )

        payload = decode_token(
            token=token,
            secret_key=settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        # Проверка срока действия
        if datetime.utcfromtimestamp(payload.get('exp')) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Refresh токен истек'
            )

        email = payload.get('sub')
        hash_to_logout = payload.get('hash_to_logout')

        if not email:
            raise  HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Недействительный email'
            )

        # Проверяем пользователя
        user = get_user(username=email, db=db)
        if not user:
            raise  HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Пользователь не найден'
            )

        # Проверяем, что пользователь не вышел
        if not user.hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Вы вышли из системы. Требуется повторная аутентификация.'
            )

        # Проверяем, что хеш совпадает
        if hash_to_logout != user.hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Недействительная сессия. Требуется повторная аутентификация.'
            )

        # Создаем новые токены
        access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": email,
                "hash_to_logout": hash_to_logout
            },
            expires_delta=access_token_expire
        )

        # Создаем refresh_token
        refresh_token = create_refresh_token(email, hash_to_logout)

        return JSONResponse({
            'result': True,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer'
        })

    except HTTPException:
        raise
    except Exception as e:
        raise  HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Ошибка на сервере'
        )


def get_current_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Она работает как зависимость,
    создадим зависимость для идентификации current_user.
    :param token: токен
    :param db: объект БД
    :return: объект пользователя
    """
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail='Не удалось подтвердить учетные данные')

    exception_logout = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                               detail='Вы вышли, авторизуйтесь')
    try:
        payload = decode_token(token=token, secret_key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        username: str = payload.get('sub')
        hash_to_logout: str = payload.get('hash_to_logout')
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username=username, db=db)

    if user is None:
        raise credentials_exception
    if hash_to_logout != user.hash:
        raise exception_logout
    return user


def authenticate_user(username: str, password: str, db: Session):
    """
    Функция проверяет наличия пользователя в БД,
    сверяет переданный пароль на соответствие,
    добавляет хеш в БД для реализации logout
    """
    user = get_user(username=username, db=db)
    if not user:
        return False
    if not Hasher.verify_password(password, user.hashed_password):
        return False
    return user
