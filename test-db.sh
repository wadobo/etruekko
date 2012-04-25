#!/bin/bash

python manage.py syncdb --noinput
python manage.py migrate

python manage.py createsuperuser

python manage.py addtestusers 20
python manage.py addtestgroups 10
python manage.py addtestitems 20

