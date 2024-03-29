# Flite

### Project Setup
To run the project locally, make sure you have docker installed on your machine, thn run the following command:

```
docker-compose up
```

### Endpoints Usage
- ```
  users/:user_id
  ```
  Request method: GET
  
  Request JSON body: Empty

- ```
  users/
  ```
  Request method: GET
  
  Request JSON body: Empty
  
- ```
  users/:user_id/deposits
  ```
  Request method: POST
  
  Request JSON body:
  ```
  {
    "amount": int
  }
  ```

- ```
  users/:user_id/withdrawals
  ```
  Request method: POST
  
  Request JSON body:
  ```
  {
    "amount": int
  }
  ```

- ```
   account/:sender_account_id/transfers/:recipient_account_id
  ```
  Request method: POST
  
  Request JSON body:
  ```
  {
    "amount": int
  }
  ```

- ```
  account/:account_id/transactions
  ```
  Request method: GET
  
  Request JSON body: Empty

- ```
  account/:account_id/transactions/:transaction_id
  ```
  Request method: GET
  
  Request JSON body: Empty

### Testing
To run the integration tests, use the command below:

```
docker-compose exec django python manage.py test flite.users.test.test_views
```

### Assumptions made during the project
- I assumed that every user has sufficient balance before making a P2P transfer.
- I created a transaction record for Deposits, Withdrawal and P2P transfers.
