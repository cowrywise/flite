# Users
Supports registering, viewing, and updating user accounts.

## Register a new user account

**Request**:

`POST` `/users/`

Parameters:

Name       | Type   | Required | Description
-----------|--------|----------|------------
username   | string | Yes      | The username for the new user.
password   | string | Yes      | The password for the new user account.
first_name | string | No       | The user's given name.
last_name  | string | No       | The user's family name.
email      | string | No       | The user's email address.

*Note:*

- Not Authorization Protected

**Response**:

```json
Content-Type application/json
201 Created

{
  "id": "6d5f9bae-a31b-4b7b-82c4-3853eda2b011",
  "username": "richard",
  "first_name": "Richard",
  "last_name": "Hendriks",
  "email": "richard@piedpiper.com",
  "auth_token": "132cf952e0165a274bf99e115ab483671b3d9ff6"
}
```

The `auth_token` returned with this response should be stored by the client for
authenticating future requests to the API. See [Authentication](authentication.md).


## Get a user's profile information

**Request**:

`GET` `/users/:id`

Parameters:

*Note:*

- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
200 OK

{
  "id": "6d5f9bae-a31b-4b7b-82c4-3853eda2b011",
  "username": "richard",
  "first_name": "Richard",
  "last_name": "Hendriks",
  "email": "richard@piedpiper.com",
}
```


## Update your profile information

**Request**:

`PUT/PATCH` `/users/:id`

Parameters:

Name       | Type   | Description
-----------|--------|---
first_name | string | The first_name of the user object.
last_name  | string | The last_name of the user object.
email      | string | The user's email address.



*Note:*

- All parameters are optional
- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
200 OK

{
  "id": "6d5f9bae-a31b-4b7b-82c4-3853eda2b011",
  "username": "richard",
  "first_name": "Richard",
  "last_name": "Hendriks",
  "email": "richard@piedpiper.com",
}
```


## Deposit Money

**Request**:

`POST` `/users/:user_id/deposits`

PayLoad:

Name       | Type   | Description
-----------|--------|---
amount | float | Amount To be Deposited.


*Note:*

- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
201 CREATED

{
  "id": "f7ba16d1-c6fb-439f-b814-ab319e78451c",
  "book_balance": 343.0912400000002,
  "available_balance": 343.0912400000002
}
```

## Withdrawal

**Request**:

`POST` `/users/:user_id/withdrawals`

PayLoad:

Name       | Type   | Description
-----------|--------|---
amount | float | Amount To be Withdrawn.


*Note:*

- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
201 CREATED

{
  "id": "f7ba16d1-c6fb-439f-b814-ab319e78451c",
  "book_balance": 43.0912400000002,
  "available_balance": 43.0912400000002
}
```

## P2P Transfer

**Request**:

`POST` `/account/:sender_account_id/transfers/:recipient_account_id`

PayLoad:

Name       | Type   | Description
-----------|--------|---
amount | float | Amount To be Transferred.


*Note:*

- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
201 CREATED

{
  "id": "f7ba16d1-c6fb-439f-b814-ab319e78451c",
  "book_balance": 3.091240000000198,
  "available_balance": 3.091240000000198
}
```

## Transaction List

**Request**: Returns A Paginated List Of User Transactions

`GET` `/account/:account_id/transactions`

*Note:*

- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
200 OK

{
    "count": 11,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "334b608d-21b3-4d12-a3a9-6e9d16bc8883",
            "created": "2021-06-08T08:34:19+0100",
            "modified": "2021-06-08T08:34:19+0100",
            "reference": "42ee4b58577a",
            "status": "success",
            "amount": 40.0,
            "new_balance": 3.091240000000198,
            "owner": "ddb259fa-3a5c-4f23-824b-efebda16d543"
        },
        {
            "id": "7bc50db0-7d8a-4cd5-9a07-2f7d3262f334",
            "created": "2021-06-08T08:31:21+0100",
            "modified": "2021-06-08T08:31:21+0100",
            "reference": "64b3d7f626af",
            "status": "success",
            "amount": 300.0,
            "new_balance": 43.0912400000002,
            "owner": "ddb259fa-3a5c-4f23-824b-efebda16d543"
        }
    ]
}
```

## Transaction Details

**Request**: Get Transaction Details

`GET` `/account/:account_id/transactions/transaction_id`

*Note:*

- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
200 OK

{
  "id": "334b608d-21b3-4d12-a3a9-6e9d16bc8883",
  "created": "2021-06-08T08:34:19+0100",
  "modified": "2021-06-08T08:34:19+0100",
  "reference": "42ee4b58577a",
  "status": "success",
  "amount": 40.0,
  "new_balance": 3.091240000000198,
  "owner": "ddb259fa-3a5c-4f23-824b-efebda16d543"
}
```