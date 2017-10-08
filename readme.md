# REST API
Python backend based on flask and SQLAlchemy. Built for a PostgreSQL database.
## Requirements
All required packages are listed in requirements.txt. Install by running
```
$ pip install -r requirements.txt
```
## Usage
### DB setup
To create the db run 
```
$ python manage.py db_create
```
### DB migrations
To migrate changes, run
To create the db run 
```
$ python manage.py db migrate
```
### DB upgrade
To upgrade to latest stored db version, run
```
$ python manage.py db upgrade
```
### Run application
To run the server in console mode, run
To create the db run 
```
$ python manage.py runserver
```