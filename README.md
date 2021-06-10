# Flite

Flite is Django Restful Wallet App API 

## Features
- Users can create accounts.
- Deposit funds via bank or card transfer.
- Users can withdraw funds to banks.
- Users can transfer funds to other user.
- Users can link card to account.
- Users can link bank account to their flite account


### Built With
* [Django](https://www.djangoproject.com/)
* [Docker](https://www.docker.com/)
* [Postgres](https://www.postgresql.org/)


## Getting Started

Now we are are the most exciting part of this documentation, 
Follow the step below to run a local version of the app. Please ensure docker is 
installed on your system or otherwise click [Get started with docker](https://www.docker.com/get-started) to install docker. 
Navigate to the directory you would link to run the app and follow the steps below: 


1. Clone the repo
   ```sh
   git clone https://github.com/cowrywise/flite
   ```
2. Create a .env environment file. Copy the values of entries below from env.example to .env file

3. Enter the command below to start docker
  ```sh
  make up
  ```
4. Create Makemigrations (Optional)
  ```sh
  make makemigrations
  ```
5. Migrate changes to database
  ```sh
  make migrate
  ```
6. Create Superuser
  ```sh
  make createsuperuser
  ```
7. Navigate to [API_DOCUMENTATION](http://localhost:8000/redoc/) to view API documentation
   or you can head straigh to the root [localhost](localhost:8000/api/v1/)

NB: All commands above are shortcut. Navigate to [MakeFile](./MakeFile) to see list of all commands

### Assumptions
- Banks and Cards services are normally handled by third party services.
    All transactions are faked and are marked successfully by defaults to
    model a pratically system 
- Withdrawals and Deposit can only be made to user owned banks and cards.
    This is to prevent unathorized withdrawal
- Due to delicate nature of all financial system, there is a strict authorization policy.
    Users can only view, edit and delete objects they owned.
- Users can deposit any amount but can not withdraw more than their current balance