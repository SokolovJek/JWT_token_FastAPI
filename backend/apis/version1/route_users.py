from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from schemas.users import UserCreate, ShowUser, UserUpdate
from db.session import get_db
from db.models.users import User
from apis.version1.route_authenticated import get_current_user_from_token
from core.user_service import UserService


router = APIRouter()


@router.post('/register', response_model=ShowUser, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя

    - **username**: Уникальное имя пользователя (минимум 3 символа)
    - **email**: Уникальный email пользователя
    - **password**: Пароль (минимум 6 символов)

    Возвращает созданного пользователя
    """
    try:
        new_user = UserService.create_user(user_data=user, db=db)
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании пользователя: {str(e)}"
        )


@router.post('/{id_user}', response_model=ShowUser)
def show_user_by_id(
    id_user: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """
    Получение пользователя по ID (только для владельца или администратора)

    - **id_user**: ID пользователя для просмотра

    Права доступа:
    - Владелец может просматривать свой профиль
    - Администратор может просматривать любого пользователя
    """
    try:
        user = UserService.get_user_by_id(
            user_id=id_user,
            current_user=current_user,
            db=db
        )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении пользователя: {str(e)}"
        )


@router.get('', response_model=ShowUser)
def show_current_user(
    current_user: User = Depends(get_current_user_from_token)
):
    """
    Получение информации о текущем авторизованном пользователе
    """
    return UserService.get_current_user_info(current_user)


@router.get('/all', response_model=List[ShowUser])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """
    Получение списка всех пользователей (только для администраторов)
    """
    try:
        users = UserService.get_all_users(
            skip=skip,
            limit=limit,
            current_user=current_user,
            db=db
        )
        return users
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении списка пользователей: {str(e)}"
        )


@router.put('/{id_user}', response_model=ShowUser)
def update_user(
    id_user: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """
    Обновление данных пользователя (только для владельца или администратора)
    """
    try:
        updated_user = UserService.update_user(
            user_id=id_user,
            user_data=user_update.dict(exclude_unset=True),
            current_user=current_user,
            db=db
        )
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении пользователя: {str(e)}"
        )

@router.delete('/{id_user}')
def delete_user(
    id_user: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """
    Удаление пользователя (только для администраторов)
    """
    try:
        success = UserService.delete_user(
            user_id=id_user,
            current_user=current_user,
            db=db
        )
        return {"message": f"Пользователь с id {id_user} успешно удален"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении пользователя: {str(e)}"
        )
