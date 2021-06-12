# Users

Supports registering, viewing, and updating user accounts.

## Register a new user account

**Request**:

`POST` `/users/`

Parameters:

| Name       | Type   | Required | Description                            |
| ---------- | ------ | -------- | -------------------------------------- |
| username   | string | Yes      | The username for the new user.         |
| password   | string | Yes      | The password for the new user account. |
| first_name | string | No       | The user's given name.                 |
| last_name  | string | No       | The user's family name.                |
| email      | string | No       | The user's email address.              |

_Note:_

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

_Note:_

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

| Name       | Type   | Description                        |
| ---------- | ------ | ---------------------------------- |
| first_name | string | The first_name of the user object. |
| last_name  | string | The last_name of the user object.  |
| email      | string | The user's email address.          |

_Note:_

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

## Deposit money for a user

**Request**:

`POST` `/users/:user_id/deposits`

PayLoad:

| Name   | Type  | Description             |
| ------ | ----- | ----------------------- |
| amount | float | Amount to be deposited. |

_Note:_

- All parameters are required
- Not Authorization Protected

**Response**:

```json
Content-Type application/json
200 OK
{
    "status": "success",
    "message": "amount deposited successfully",
    "data": {
        "first_name": "emeka",
        "last_name": "olorondu",
        "available_balance": 16800.0
    }
}
```

## Withdraw money from a user's account

**Request**:

`POST` `/users/:user_id/withdrawals`

PayLoad:

| Name   | Type  | Description             |
| ------ | ----- | ----------------------- |
| amount | float | Amount to be withdrawn. |

_Note:_

- All parameters are required
- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
200 OK
{
    "status": "success",
    "message": "amount withdrawn successfully...no more insufficient funds😀",
    "data": {
        "first_name": "emeka",
        "last_name": "olorondu",
        "available_balance": 16400.0
    }
}
```

## Transaction list (single user)

**Request**: Retrieves the list of all transactions made by a user

`GET` `/account/:account_id/transactions`

_Note:_

- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
200 OK
{
    "status": "success",
    "message": "user transactions retrieved successfully",
    "data": [
        {
            "id": "c0c77812-f145-4f23-b07d-5e2fef848cbc",
            "created": "2021-06-12T11:21:57+0100",
            "modified": "2021-06-12T11:21:57+0100",
            "reference": "a533409d478e",
            "status": "success",
            "amount": 200.0,
            "new_balance": 16400.0,
            "owner": "3d6ab92e-30ed-44b0-8673-8e5e156e174e"
        },
        {
            "id": "a8487248-a395-47d3-804d-2ea5d3c0a145",
            "created": "2021-06-12T11:20:29+0100",
            "modified": "2021-06-12T11:20:29+0100",
            "reference": "2c9f093fb3ef",
            "status": "success",
            "amount": 200.0,
            "new_balance": 16600.0,
            "owner": "3d6ab92e-30ed-44b0-8673-8e5e156e174e"
        },
        {
            "id": "72f862c6-a1bc-4e4f-a5b0-903a9179fab9",
            "created": "2021-06-12T11:14:06+0100",
            "modified": "2021-06-12T11:14:06+0100",
            "reference": "e15ad3c35373",
            "status": "success",
            "amount": 500.0,
            "new_balance": 16800.0,
            "owner": "3d6ab92e-30ed-44b0-8673-8e5e156e174e"
        }
    ]
}
```

## Transaction details (single user)

**Request**: Retrieve details of a single transaction performed by a user

`GET` `/account/:account_id/transactions/transaction_id`

_Note:_

- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
200 OK
{
  "status": "success",
  "message": "user transaction retrieved successfully",
  "data": {
    "id": "3ec50dc0-7d5a-9ee7-2b47-4f3c3543c213",
    "created": "2021-06-11T13:45:22+0100",
    "modified": "2021-06-11T13:45:22+0100",
    "reference": "64c3d4a646ce",
    "status": "success",
    "amount": 150.0,
    "new_balance": 100.0223400000001,
    "owner": "efb213fe-5c5e-3b10-399e-ccbede14d543"
  }
}
```

## P2P Transfer

**Request**: allows for transfer of money between users

`POST` `/account/:sender_account_id/transfers/:recipient_account_id`

PayLoad:

| Name   | Type  | Description               |
| ------ | ----- | ------------------------- |
| amount | float | Amount to be transferred. |

_Note:_

- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
200 OK
{
  "status": "success",
  "message": "transfer successful",
  "data": {
    "id": "3ec50dc0-7d5a-9ee7-2b47-4f3c3543c213",
    "book_balance": 100.0223400000001,
    "available_balance": 100.0223400000001
  }
}
```
