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

## Get all Users

**Request**:

`GET` `/users/`

_Note:_

- All parameters are optional
- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
200 OK

{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "7ec88f5a-230b-4c0b-857d-b893e3fd13aa",
      "username": "vasilias",
      "first_name": "",
      "last_name": "",
      "email": "",
      "auth_token": "235198b27da711470722616ba30faa3529aecf7c"
    },
    {
      "id": "a8f0cb87-4145-4e0d-b71c-c79cfaac35e1",
      "username": "el-joft",
      "first_name": "King",
      "last_name": "",
      "email": "ottimothy@gmail.com",
      "auth_token": "3dfbdec41c1bb4ef17e4a21e2fd4e7b46f04722d"
    },
    {
      "id": "236c5404-7e72-4a0d-92b9-41d53c3c4c2f",
      "username": "testuser0",
      "first_name": "Jamie",
      "last_name": "Miller",
      "email": "warejoseph@gmail.com",
      "auth_token": "adb992e2e1c2c3c102729c6ee013773b3a32df52"
    },
    {
      "id": "f6ce6787-9ca4-4b48-bd18-c5598ab5b382",
      "username": "testuser1",
      "first_name": "Meredith",
      "last_name": "Garcia",
      "email": "jeffrey69@jennings.info",
      "auth_token": "ac010520121ee4a5e752cc8d8a36d9540d823afc"
    }
  ]
}
```

## Deposits

**Request**:

`POST` `/users/:user_id/deposits/`

Parameters:

| Name   | Type  | Description            |
| ------ | ----- | ---------------------- |
| amount | float | The Amount to deposit. |

_Note:_

- All parameters are required
- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
200 OK

{
  "status": "success",
  "message": "Your Deposit Request was Successful",
  "data": {
    "id": "fd5b3212-6379-4c5a-baf4-349a9dc33fe0",
    "owner": {
      "id": "a8f0cb87-4145-4e0d-b71c-c79cfaac35e1",
      "username": "el-joft",
      "first_name": "King",
      "last_name": ""
    },
    "book_balance": 500000.0,
    "available_balance": 503000.0
  }
}
```

## Withdrawals

**Request**:

`POST` `/users/:user_id/withdrawals/`

Parameters:

| Name   | Type  | Description            |
| ------ | ----- | ---------------------- |
| amount | float | The Amount to deposit. |

_Note:_

- All parameters are required
- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
200 OK

{
  "status": "success",
  "message": "Your Withdrawal Request was Successfully",
  "data": {
    "id": "fd5b3212-6379-4c5a-baf4-349a9dc33fe0",
    "owner": {
      "id": "a8f0cb87-4145-4e0d-b71c-c79cfaac35e1",
      "username": "el-joft",
      "first_name": "King",
      "last_name": ""
    },
    "book_balance": 500000.0,
    "available_balance": 503000.0
  }
}
```
