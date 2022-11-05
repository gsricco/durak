FROM python:3.10-alpine
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install gunicorn
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "configs.wsgi:application"]
#CMD ["python", "manage.py", "runserver"]
