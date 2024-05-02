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

2. Open your web browser and navigate to: `http://0.0.0.0:8000/docs/`

   This will display the Redoc UI, where you can explore the available API endpoints, view request and response schemas, To interact with the API navigate to `http://0.0.0.0:8000/api/playground/` 
   To see all the endpoints, create a superuser account and login to the admin, then refresh the docs to see the rest of the endpoints that are protected.

### Available endpoints
Sure! Here's a list of the available endpoints based on the provided code:

1. Budget Category List:
   - URL: `/budget_categories/`
   - Methods:
     - GET: Retrieve a list of budget categories for the authenticated user.
     - POST: Create a new budget category for the authenticated user.

2. Budget Category Detail:
   - URL: `/budget_categories/<int:pk>/`
   - Methods:
     - GET: Retrieve details of a specific budget category.
     - PUT: Update a specific budget category.
     - DELETE: Delete a specific budget category.

3. Transaction List:
   - URL: `/transactions/`
   - Methods:
     - GET: Retrieve a list of transactions for the authenticated user.
     - POST: Create a new transaction for the authenticated user.

4. Transaction Detail:
   - URL: `/transactions/<int:pk>/`
   - Methods:
     - GET: Retrieve details of a specific transaction.
     - PUT: Update a specific transaction.
     - DELETE: Delete a specific transaction.

Note that these endpoints require authentication using token-based authentication. Users need to provide a valid token in the request headers to access these endpoints. For example
```bash
curl -X POST \
  -H "Authorization: Token your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "Food",
        "description": "Budget for groceries and dining out",
        "max_spend": 500.00
      }' \
  http://localhost:8000/budget_categories/
  ```

## Running Tests

To run the test suite for the Flite project, use the following command in another terminal/tab:

```
docker-compose exec django python manage.py test
```

This command will execute the test cases defined in the Django application and provide the test results.

