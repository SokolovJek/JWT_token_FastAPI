# fast_api_test_task
Создание Api с использованием фреймворка FastAPI.

Задание:
Разработать REST API аутентификации пользователей по jwt токену. Фреймворк на свой выбор, но желательно использовать Flask или FastAPI.
В качестве данных пользователя использовать любой логин, пароль и имя пользователя
Необходимые эндпойнты:
- POST /login – аутентификация пользователя по логину и паролю, при успешном вводе возвращаем jwt и refresh_token
- POST /logout – выход пользователя
- POST /refresh_jwt – обновление токена по refresh_token
- GET /user – вывод информации о пользователе (только для аутентифицированного пользователя, для не аутентифицированных пользователей возвращаем ошибку 401)

Реализация:

Для запуска приложения:
1) создаем виртуальное окружение: python3 -m venv env
2) входим в него: source env/bin/activate
3) pip install -r requirements.txt
4) указываем нужную БД.
   - если PostgreSql В файле .env указываем актуальные креды.
   - если SQLite в файле backend/db/session.py раскомментируем строки с SQLite и закомментировать PostgreSql
5) переходим в директорию: cd backend
6) вводим команду uvicorn main:app --reload


Для запуска тестов:
1) переходим в директорию: cd backend
2) вводим команду pytest

Для просмотра всех доступных end-point:
1) запускаем приложение
2) переходим по ссылке http://127.0.0.1:8000/docs

Для реализации logout на стороне backend:
1) использовал хеш вставленный в токен. Если пользователь входит, то создается хеш и сохраняется в БД и в токен. При выходе хеш с БД удаляется. При просмотре end-poit на которых необходима авторизация, проверяем соответствие хеша с токена и с БД.


Иерархия папок:

backend/

├─.env                  # креды

├─apis/
│ ├─base.py                  # главный маршрутизатор

│ └─version1/

│       ├─route_general_pages.py         # end-points

│       ├─route_authenticated.py         # end-points

│       └─route_users.py                 # end-points

├─db/

│ ├─base.py

│ ├─base_class.py

│ ├─black_list.py

│ ├─models/

│ │ └─users.py

│ ├─repository

│ | ├─login.py

│ │ └─users.py

│ └─session.py

├─main.py

├─schemas/

│ ├─tokens.py

│ └─users.py

├─tests/

│ ├─conftest.py

│ ├─utils/

│ | └─users.py

│ └─test_routes/

│   └─test_users.py

├─test_db.db

├─static/

│ └─images/

│   └─logo.png

└─templates/

  ├─--components/

  │    └─navbar.html

  ├─general_pages/

  │ └─homepage.html

  └─shared/

        └─base.html

