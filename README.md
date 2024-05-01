# Flite

## Features

- RESTful API endpoints for seamless integration with frontend applications
- User authentication and authorization using Django's built-in authentication system
- Asynchronous task processing with Celery and RabbitMQ
- Dockerized development environment for easy setup and deployment
- Comprehensive test suite for ensuring code quality and reliability
- Integration with [Mailpit](https://github.com/axllent/mailpit) for capturing outgoing emails during development
- Monitoring and administration of Celery tasks using Flower

## Prerequisites

Before getting started with Flite, ensure that you have the following prerequisites installed on your system:

- Docker: [Install Docker](https://docs.docker.com/get-docker/)
- Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

To set up the Flite project on your local machine, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/smyja/flite.git
   ```

2. Navigate to the project directory:
   ```
   cd flite
   ```

3. Create a `.env` file in the project root and provide the necessary environment variables, example variables are in the `.env.example` file.

4. Build and start the Docker containers:
   ```
   docker-compose up --build
   ```
   This command will build the required Docker images and start the containers defined in the `docker-compose.yml` file.

5. Run database migrations:
   Open another terminal and run the following commands
   ```
   docker-compose exec django python manage.py makemigrations
   ```
   and
   
   ```
   docker-compose exec django python manage.py migrate
   ```

   This command will apply the database migrations and set up the required tables.

### Access the application:
   - Django server: http://0.0.0.0:8000
   - Mailpit: http://0.0.0.0:8025
   - Flower: http://0.0.0.0:5555

## API Documentation

The API documentation for Flite is generated using drf-yasg, a Swagger generation tool for Django REST Framework. To access the API documentation, follow these steps:

1. Start the Django development server:
   ```
   docker-compose up
   ```

2. Open your web browser and navigate to: http://0.0.0.0:8000/docs/

   This will display the Swagger UI, where you can explore the available API endpoints, view request and response schemas, and interact with the API.

## Running Tests

To run the test suite for the Flite project, use the following command in another terminal/tab:

```
docker-compose exec django python manage.py test
```

This command will execute the test cases defined in the Django application and provide the test results.

