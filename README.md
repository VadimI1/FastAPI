# Веб-приложение на Python с использованием FastAPI
## Стек технологий
1. Python == 3.9
2. fastapi == 0.111.0
3. uvicorn == 0.30.1
4. replit == 4.0.0
5. starlette == 0.37.2
6. uvicorn == 0.30.1
7. python-jose == 3.3.0
8. passlib == 1.7.4
9. sqlalchemy == 2.0.31
10. pydantic == 2.8.2
11. bcrypt == 4.0.1
12. FastAPI-SQLAlchemy  == 0.2.1
13. python-dotenv == 1.0.1
14. pytest == 8.2.2
15. psycopg2 == 2.9.9
16. alembic == 1.13.2
17. asyncpg == 0.29.0
18. minio == 7.2.7
## Функционал
1. GET/memes: Получить список всех мемов
2. GET/memes/{id}: Получить конкретный мем по его ID
3. POST/memes: Добавить новый мем
4. PUT/memes/{id}: Обновить существующий мем
5. DELETE/memese/{id}: Удалить мем
6. POST/signup: Регистрация
7. POST/login: Система для авторизации
## Запуск
1. Склонировать репозиторий
2. Создать базу данных в PostgreSQL
```env
CREATE DATABASE mem;
```
3. Создать и запустить Docker 
```env
docker-compose up --build
```
4. Перейти по URL: http://localhost:8000/docs
5. Для запуска unit-тестов необходимо зарегестрировать 
пользователя email: asdf@mail.ru пароль: asdf и выполнить следующие
команды.
```env
 docker-compose exec pytest bash
 pytest
```
## Работа с Swagger
Для полного доступа к функционалу необходимо зарегистрироваться
и авторизировать. "/signup" отвечает за регистрацию. Для авторизации необходимо
нажать на кнопку Authorize.
## Работа с MinIO
После развертывания Docker необходимо перейти по URL указоному в Docker.
Логин и пароль для авторизации: minioadmin minioadmin.