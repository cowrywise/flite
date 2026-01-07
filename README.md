# Flite

Cowrywise Backend Engineering Assessment - A Django REST API project for evaluating backend engineering candidates.

## Overview

Flite is a recruitment test repository designed to assess candidates' proficiency with Django, REST APIs, and backend development best practices.

## Tech Stack

- **Framework**: Django / Django REST Framework
- **Database**: PostgreSQL
- **Containerization**: Docker & Docker Compose
- **Deployment**: Heroku-ready (Procfile included)

## Getting Started

### Prerequisites

- Python 3.x
- Docker & Docker Compose (recommended)
- PostgreSQL

### Local Development with Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/cowrywise/flite.git
   cd flite
   ```

2. Copy the environment file:
   ```bash
   cp env.example .env
   ```

3. Start the application:
   ```bash
   docker-compose up --build
   ```

The API will be available at `http://localhost:8000`

### Local Development without Docker

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy and configure environment variables:
   ```bash
   cp env.example .env
   # Edit .env with your database credentials
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Running Tests

```bash
python manage.py test
```

With coverage:
```bash
coverage run manage.py test
coverage report
```

## Project Structure

```
flite/
├── flite/              # Main Django application
├── docs/               # Documentation
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
└── Procfile           # Heroku deployment configuration
```

## Contributing

Please refer to the documentation in the `docs/` folder for assessment guidelines and contribution instructions.
