# Flite

## Brief Description

Flite is a simple wallet application that allows users to perform the following operations:

- Deposit money
- Withdraw money
- Transfer money between users
- View transactions made for each user

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development purposes.

### Prerequisites

System requirements for this project to work includes:

- Git
- Python/Python3
- virtualenv
- Docker (optional)
- Postgres (optional)
- Any IDE of your choice (VS Code is recommended)
  `

### Running the project

To run the project on your local machine, follow the steps below:

- Clone this repo and navigate to the project folder
- Create a virtual environment using this command on your terminal

```bash
vitrualenv venv
```

- Activate the virtual environment using this command:
  Mac:

```bash
source env/bin/activate
```

Windows

```bash
source env/Scripts/activate
```

- From your IDE, select the **python.exe** file contained in `venv/Scripts` (Windows) or `venv/bin` (Mac) folder. This will enable the installed packages to be used in thr application.

- Install the dependencies in the **requirements.txt** file by running the following command:

```bash
pip install -r requirements.txt
```

- Create a **.env** file in the root directory of your project and populate it with the required data, as described in the **env.sample** file

- To create the required tables in the database, run the migrations with the following command:

```bash
python manage.py migrate
```

- After the above steps have been followed, start the server with the following command:

```bash
python manage.py runserver
```

Alternatively, if you want to use Docker for the project, ignore the steps above, navigate to the project directory and run the following commands on the terminal:

```bash
docker-compose up -d
```

## Unit Testing

For automated testing, run the following command:

```bash
python manage.py test
```
