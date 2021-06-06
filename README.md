# Flite
Main => ![example workflow](https://github.com/iamr0b0tx/flite/actions/workflows/ci.yml/badge.svg) <br>

# Setup and Installation
## Prerequisites
- Python 3.6 [Download](https://www.python.org/downloads/)
- Docker (and docker compose)

## Run the Project
1. Clone the repository
1. Create a file named `.env` and add the contents in [env.example](./env.example)
1. Make sure your docker service is running. Run the project by calling docker-compose
    ```
        docker-compose up
    ```
1. visit [127.0.0.1:8000](http://127.0.0.1:8000) in a web browser

## Test the project
1. Start the containers in detached mode
    ```
        docker-compose up -d
    ```
1. Run all the tests
    ```
        docker-compose run django python manage.py test    
    ```
   or just some of the tests
   ```
        docker-compose run django python manage.py test flite.users.test.test_views
    ```
 
# Documentation

**Request**:
`POST` `/users/:user_id/deposits`

Parameters:

Name       | Type   | Required | Description
-----------|--------|----------|------------
user_id    | float  | Yes      | The id of a User.

Body:

Name       | Type   | Required | Description
-----------|--------|----------|------------
amount     | float  | Yes      | The amount to deposit.


*Note:*
- Not Authorization Protected
- It funds a user by adding a credit transaction to the Transaction model where owner is user_id

**Response**:
```
Content-Type "application/json"
201 Created

{
  "status": true,
  "message": "Amount Deposited successfully"
}
```


**Request**:
`POST` `/users/:user_id/withdrawals`

Parameters:

Name       | Type   | Required | Description
-----------|--------|----------|------------
user_id    | float  | Yes      | The id of a User.

Body:

Name       | Type   | Required | Description
-----------|--------|----------|------------
amount     | float  | Yes      | The amount to deposit.

*Note:*
- **[Authorization Protected](./docs/api/authentication.md)** The user_id must match the authenticated user
- It funds a user by adding a credit transaction to the Transaction model where owner is user_id. A debit is represented as a negative amount.

**Response**:
```
Content-Type "application/json"
200 OK

{
  "status": true,
  "message": "Amount Withdrawn successfully"
}
```

**Request**:
`POST` `/account/:sender_account_id/transfers/:recipient_account_id`

Parameters:

Name                  | Type   | Required | Description
----------------------|--------|----------|------------
sender_account_id     | float  | Yes      | The user id of the sender.
recipient_account_id  | float  | Yes      | The user id of the recipient.

Body:

Name       | Type   | Required | Description
-----------|--------|----------|------------
amount     | float  | Yes      | The amount to deposit.

*Note:*
- **[Authorization Protected](./docs/api/authentication.md)** The sender_account_id must match the authenticated user
- This creates an entry in the P2PTransfer model where sender_account_id is the sender and recipient_account_id is the recipient (as User objects)

**Response**:
```
Content-Type "application/json"
200 OK

{
  "status": true,
  "message": "Transfer was successful"
}
```

**Request**:
`GET` `/account/:account_id/transactions`

Parameters:

Name       | Type   | Required | Description
-----------|--------|----------|------------
account_id | float  | Yes      | The id of the user AKA transaction owner.

*Note:*
- **[Authorization Protected](./docs/api/authentication.md)** The account_id must match the authenticated user
- This endpoint retrieves data from the Transaction Model filtering with account_id as owner

**Response**:
```
Content-Type "application/json"
200 OK

{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "b0440902-8771-4138-9f59-582791c9bed7",
            "created_on": "2021-06-06T16:25:00+0100",
            "modified_on": "2021-06-06T16:25:00+0100",
            "reference": "deposit",
            "status": "deposited",
            "amount": 150.25,
            "owner": "33ced359-8df2-47f8-baf3-59f6cb491321"
        },
        {
            "id": "9c5b7bc4-6568-4039-a703-1bdac0fa0668",
            "created_on": "2021-06-06T16:11:33+0100",
            "modified_on": "2021-06-06T16:11:33+0100",
            "reference": "deposit",
            "status": "deposited",
            "amount": 100.0,
            "owner": "33ced359-8df2-47f8-baf3-59f6cb491321"
        }
    ]
}
```

**Request**:
`GET` `/account/:account_id/transactions/:transaction_id`

Parameters:

Name           | Type   | Required | Description
---------------|--------|----------|------------
account_id     | float  | Yes      | The id of the user AKA transaction owner.
transaction_id | float  | Yes      | The transaction Id.

*Note:*
- **[Authorization Protected](./docs/api/authentication.md)** The account_id must match the authenticated user
- This endpoint retrieves data from the Transaction Model filtering with account_id as owner and as transaction_id

**Response**:
```
Content-Type "application/json"
200 OK

{
    "id": "b0440902-8771-4138-9f59-582791c9bed7",
    "created_on": "2021-06-06T16:25:00+0100",
    "modified_on": "2021-06-06T16:25:00+0100",
    "reference": "deposit",
    "status": "deposited",
    "amount": 150.25,
    "owner": "33ced359-8df2-47f8-baf3-59f6cb491321"
}
```

