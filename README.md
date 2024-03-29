# Flite

### Project Setup
To run the project locally, make sure you have docker installed on your machine, thn run the following command:

```
docker-compose up
```

### Testing
To run the integration tests, use the command below:

```
docker-compose exec django python manage.py test flite.users.test.test_views
```

### Assumptions made during the project
- I assumed that every user has sufficient balance before making a P2P transfer.
