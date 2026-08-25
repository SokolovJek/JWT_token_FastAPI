from passlib.context import CryptContext


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class Hasher:
    """
    Здесь будет логика создания хеша из пароля и сравнивания паролей,
    Также здесь создается хеш, для реализации logout(end point /logout)
    """

    @staticmethod
    def verify_password(plain_password, hashed_password):
        """
        Сравнивает пароль и хэш
        :param plain_password: пароль
        :param hashed_password: хэш-пароля
        :return: boolean
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        """
        Выдает хэш из переданного в метод пароля
        :param password: пароль
        :return: хэш из пароля
        """
        return pwd_context.hash(password)

    @staticmethod
    def get_hash_to_realize_function_logout(data: str):
        """
        Создает хэша для end-point /logout
        :param data: str = данные для хеша
        :return: str = хэш из пароля
        """
        return pwd_context.hash(data)

    @staticmethod
    def compare_hashes(plain_data, hashed_data):
        """
        Сравнивает даные и хэш для end-point /logout
        :param plain_data: str = даные
        :param hashed_data:str = хэш-данных
        :return: boolean
        """
        return pwd_context.verify(plain_data, hashed_data)
