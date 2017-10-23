#!/usr/bin/env bash
sudo apt-get -y update
sudo apt-get -y install python2.7
sudo apt install -y python-pip
pip install django==1.9
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

