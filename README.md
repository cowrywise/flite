# Flite

### How To Set up and run

* Install python version 3 from [here](https://www.python.org/downloads/)
* Clone this repo to your local computer
* Open project in your favourite IDE
* Open a Terminal in your IDE
* Change directory into the base project directory `cd flite`, do this if this is not dne by the IDE
* Set up your `venv` as this is recommended for local development, so you do not pollute your python installation

  #### Venv setup
    * `python3 -m venv venv` this will create the venv directory if it doesn't exist, and also create directories inside
      it containing a copy of the Python interpreter, the standard library, and various supporting files
    * Activate the virtual environment:
        * `venv\Scripts\activate.bat` - windows
        * `sourc venv/bin/activate` - Unix or MacOS

* Once your `venv` is activated, just install your projects requirements found in the `requirements.txt` file
  with `pip install -r requirements.txt`
* This part is done to make sure your IDE can help with intellisense when you are working locally
  #### Docker and docker-compose set up
    * Install [docker](https://docs.docker.com/engine/install/ubuntu/)
      and [docker-compose](https://docs.docker.com/compose/install/)
    * Start docker if it is not already started

* In your base project folder, make a `.env` file and use the `env.example` file as a guide as to what to fill in the
  actual `env` file you just created
* Build the container using `docker-compose build`
* Run the project with `docker-compose up`
* Create a **super admin** with `docker-compose run --rm flite-django sh -c "python manage.py createsuperuser"`

## Project Assumptions

* Deposits are made to an account without a defined source. i.e You can deposit an account without a valid source.
* Transfers are Peer2Peer transfers.
* Banks were totally ignored, as I do not have access to 3rd party API to make define a bank for a user.
* The first referral code is created when the super-admin is created,
  visit [http://127.0.0.1:8009/admin/users/userprofile/](http://127.0.0.1:8009/admin/users/userprofile/) to get the
  referral code when the admin is created.
* A custom pagination is made just to justify the requirements of `page` and `limit` from the assessment.

## Running Test
* To run test, open your terminal, and run `docker-compose run --rm flite-django sh -c "python manage.py test"`

## Running Linting with Flake8
* To run your linting run `docker-compose run --rm flite-django sh -c "flake8"`

## Docs
* Check the docs in the `docs` folder, updated with the transaction resource named `transaction.md`
