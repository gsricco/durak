# durak_rulles
Quick start
Repository durak_rulles :


If you use https: https://github.com/ITec-Company/durak_rulles.git

Enter next command:

python3 -m venv venv

source venv/bin/activate(for MacOs/Linux)


. venv/Scripts/activate(for Windows)

pip install -r requirements.txt

pip install channels-redis=3.4.1

pip install channels==4.0.0

pip install daphne==4.0.0

python manage.py makemigrations


python manage.py migrate

Create admin:


python manage.py createsuperuser

Username: admin


Email: not necessary
Password: admin

Confirm password: admin

Run server:

python manage.py runserver

To run Celery tasks:

celery -A configs flower beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

celery -A configs beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

celery -A configs worker --loglevel=info
