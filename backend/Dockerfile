FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Установите рабочую директорию внутри контейнера
WORKDIR /app

# Скопируйте файл зависимостей в рабочую директорию
COPY requirements.txt requirements.txt

# Установите зависимости проекта
RUN pip install --no-cache-dir -r requirements.txt

# Скопируйте все файлы проекта в рабочую директорию
COPY . /app
RUN SECRET_KEY=something python manage.py collectstatic --noinput
# Укажите команду для запуска вашего приложения
CMD ["python", "-m", "gunicorn", "-b", "0.0.0.0:8080", "star_burger.wsgi:application"]
#CMD ["gunicorn", "--bind", "0.0.0.0:8080", "star_burger.wsgi:application"]


