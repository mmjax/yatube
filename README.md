# YaTube
Социальная сеть
### Описание
Благодаря этому проекту можно публиковать изменять удалять посты и загружать к ним фотографии, оставлять комментарии под постами и подписываться на понравившихся авторов.
### Технологии
Python, Django.
### Запуск проекта в dev-режиме
- Клонировать репозиторий и перейти в него в командной строке:
- Установите и активируйте виртуальное окружение:
```
python -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip
```
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
```
- Перейдите в каталог с файлом manage.py выполните команды:
Выполнить миграции:
```
python manage.py migrate
```
Создайте супер-пользователя:
```
python manage.py createsuperuser
```
Запуск проекта:
```
python manage.py runserver
```
