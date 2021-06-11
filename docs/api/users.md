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
201 CREATED
{
  "status": "success",
  "message": "amount deposited successfully",
  "data": {
    "first_name": "",
    "last_name": "",
    "available_balance": ""
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
201 CREATED
{
  "status": "success",
  "message": "amount withdrawn successfully...no more insufficient funds😀",
  "data": {
    "first_name": "",
    "last_name": "",
    "available_balance": ""
  }
}
```
