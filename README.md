# Flite

# How to Setup
**Step 1**: Setup python virtual environment using
```bash
python3 -m venv env
```
or using your prefered tool for creating virtual environment

**Step 2**: Install application dependency by running the below command in your activated virtual environment
```bash
pip install -r requirements.txt
```
or for a more detail installation with precise version of all the dependencies used, use the below command
```bash
pip install -r requirements.ini
```
*Note*: for Linux(Ubuntu) users you can all install the dependency with the following command if the above mentioned doesn't work for you.
```bash
cat requirements.txt | xargs -n 1 pip install
```
## Note: Install on Linux (Ubuntu)
Install postgresql dependency if you encounter compilation error with psycopg2-binary

```bash
sudo apt-get install libpq-dev
```

**Step 3**: Run server using the below command in the activated environment
```bash
python manage.py runserver
```
App should be running on http://localhost:8000

# Testing
To run test for the project, run the below command
```bash
python manage.py test
```
That should run the test runner configured for Django

# Assumption
Throughout the course of development of this app, here are some of the assumptions made:

- Every action being made to a user account should have a log or trace of it in history, hence I assumed this should be generally called Transaction history. They can be of different type, DEPOSIT, WITHDRAWAL and TRANSFER which clearly diferentiates between the types.

- A user can have multiple accounts if they wish to, in the design of my model, there's provision for that. But the API doesn't provide functionality for that. Therefore in the future, implementation wouldn't require making much adjustments to the models.

- Also for the design of the /account/:account_id/transactions/ endpoint I considered implementing it as a sub-resource under account, therefore making it easy, taking advantage of django ORM and rest_framework to implement sub-route under account viewset.
