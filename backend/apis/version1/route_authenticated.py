from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi import Depends, APIRouter, Request, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from db.session import get_db
from schemas.tokens import Token
from core.auth_service import AuthService


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')


@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Аутентификация пользователя и выдача токенов
    """
    user, access_token, refresh_token = AuthService.login(
        email=form_data.username,
        password=form_data.password,
        db=db
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Некорректный логин или пароль',
        )

    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'refresh_token': refresh_token
    }


@router.post('/logout')
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Выход пользователя из системы
    """
    # Получаем пользователя
    user = AuthService.get_current_user(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Не удалось подтвердить учетные данные'
        )

    # Выполняем logout
    success = AuthService.logout(user, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Ошибка при выходе из системы'
        )

    return JSONResponse({"message": "Вы успешно вышли"})


@router.post('/refresh_jwt')
async def refresh(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Обновление токенов
    """
    try:
        # Получаем refresh_token из запроса
        form = await request.json()
        refresh_token = form.get('refresh_token')

        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Refresh token не предоставлен'
            )

        # Обновляем токены
        access_token, new_refresh_token = AuthService.refresh_tokens(
            refresh_token=refresh_token,
            db=db
        )

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Недействительный токен'
            )

        return JSONResponse({
            'result': True,
            'access_token': access_token,
            'refresh_token': new_refresh_token,
            'token_type': 'bearer'
        })

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Ошибка на сервере'
        )


def get_current_user_from_token(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Зависимость для получения текущего пользователя
    """
    user = AuthService.get_current_user(token, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Не удалось подтвердить учетные данные'
        )

    return user
