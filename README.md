# Flite

This repository contains the source code for Flite backend API.

## Technologies

Below is a list of technologies used to build this project

* Django
* Django Rest Framework
* Docker

## Installation

Follow these steps to set up the app.

Clone the repo:

```bash
$ git clone https://github.com/el-Joft/flite.git
```

Navigate to the project directory:

```bash
$ cd flite
```
To run Locally without Docker

Create a virtual environment by running

```bash
$ pip install virtualenv
$ virtualenv venv
```

This will generate the virtual environment but will not activate it
To activate the virtual environment, run:

```bash
$ source venv/bin/activate
```
Create a `.env` file. Update it with what is in the `.env.example`


## Running and Development

To Run with Docker run

```bash
$ docker compose up
```
To run Locally

Install Dependencies

 ```bash
$ pip install -r requirements.txt
```

Start the App Locally with

 ```bash
$ python manage.py runserver
```

## Database

```bash
$ python manage.py makemigrations
$ python manage.py migrate
```

When the data is successfully migrated

## Running Tests
To run test locally.. 
```bash
$ python manage.py test
```

Check the APIs at

`http://localhost:8000/`

#### Author

> Omotayo Timothy 
> @el-joft
> ottimothy@gmail.com




