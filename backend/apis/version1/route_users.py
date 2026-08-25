from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from schemas.users import UserCreate, ShowUser
from db.session import get_db
from db.repository.users import create_new_user, retrieve_user
from db.base import User
from apis.version1.route_authenticated import get_current_user_from_token


router = APIRouter()


@router.post('/register', response_model=ShowUser)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Создание пользователя"""
    user = create_new_user(user=user, db=db)
    return user


@router.post('/{id_user}', response_model=ShowUser)
def show_user_by_id(id_user: int,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user_from_token)
                    ):
    """
    получение пользователя по id
    """

    user = retrieve_user(id_user=id_user, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Пользователя с идентификатором {id_user} не существует')
    if user.id == current_user.id or current_user.is_superuser:
        return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Вам не разрешено просматривать пользователя с id № {id_user},"
                               f" так как вы не владелец учетной записи № {id_user}!!!!"
                        )


@router.get('', response_model=ShowUser)
def show_user(current_user: User = Depends(get_current_user_from_token)):
    """
    Вывод информации о пользователе
    """
    return current_user
