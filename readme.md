# TeamFinder

TeamFinder — Django-веб-приложение для поиска единомышленников для pet-проектов. Пользователи могут регистрироваться, публиковать идеи проектов, присоединяться к чужим проектам, добавлять проекты в избранное и искать участников платформы.

В проекте реализован вариант 1: избранное и фильтрация пользователей.

## Возможности

- регистрация пользователей по имени, фамилии, email и паролю;
- вход и выход по email и паролю;
- публичные профили пользователей с контактами, аватаром, описанием и проектами;
- редактирование профиля и смена пароля;
- создание, редактирование и завершение проектов;
- участие в чужих проектах;
- список проектов с пагинацией по 12 карточек;
- список пользователей с пагинацией по 12 карточек;
- добавление и удаление проектов из избранного;
- страница избранных проектов;
- фильтрация пользователей по критериям варианта 1;
- админ-панель Django.

## Технологии

- Python 3.10+
- Django 5.2.4
- PostgreSQL 16
- Docker Compose
- Pillow
- python-decouple
- pytest
- flake8

## Локальный запуск

Склонируйте репозиторий и перейдите в папку проекта:

```bash
git clone <адрес вашего репозитория>
cd team-finder-ad
```

Создайте и активируйте виртуальное окружение:

```bash
python3 -m venv venv
source venv/bin/activate
```

Для Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

Создайте `.env` на основе примера:

```bash
cp .env_example .env
```

В `.env` указаны значения для локального запуска с Docker Compose. Основные параметры:

```env
POSTGRES_DB=team_finder
POSTGRES_USER=team_finder
POSTGRES_PASSWORD=team_finder
POSTGRES_HOST=localhost
POSTGRES_PORT=5436
TASK_VERSION=1
```

Запустите PostgreSQL:

```bash
docker compose up -d
```

Примените миграции:

```bash
python manage.py migrate
```

Создайте тестовые данные:

```bash
python manage.py seed_data
```

Создайте суперпользователя при необходимости:

```bash
python manage.py createsuperuser
```

Запустите сервер:

```bash
python manage.py runserver
```

Откройте сайт:

```text
http://localhost:8000
```

## Тестовый аккаунт

После выполнения `python manage.py seed_data` доступен пользователь:

```text
email: maria@yandex.ru
password: password
```

Команда также создаёт ещё несколько пользователей, проекты, избранное и участников проектов.

## Основные адреса

```text
/                         -> редирект на /project/list/
/project/list/            -> список проектов по заданию
/projects/list/           -> дополнительный адрес списка проектов
/projects/favorites/      -> избранные проекты текущего пользователя
/projects/create-project/ -> создание проекта
/projects/<id>/           -> страница проекта
/projects/<id>/edit/      -> редактирование проекта
/users/list/              -> список пользователей
/users/register/          -> регистрация
/users/login/             -> вход
/users/logout/            -> выход
/users/<id>/              -> профиль пользователя
/users/edit-profile/      -> редактирование профиля
/users/change-password/   -> смена пароля
/admin/                   -> админ-панель
```

## Проверка проекта

Проверка Django:

```bash
python manage.py check
```

Проверка стиля кода:

```bash
flake8 .
```

Запуск тестов:

```bash
pytest
```

Для быстрой проверки без PostgreSQL можно временно использовать SQLite:

```bash
USE_SQLITE=True python manage.py migrate
USE_SQLITE=True python manage.py seed_data
USE_SQLITE=True python manage.py runserver
```

Основной режим проекта по умолчанию использует PostgreSQL.

## Примечания для ревьюера

Выбран только вариант 1. Функции вариантов 2 и 3 не реализуются: в проекте нет управления навыками пользователей или навыками проектов. На главной странице доступен список проектов и добавление в избранное, на странице пользователей доступна фильтрация по четырём критериям варианта 1.
