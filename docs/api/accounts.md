# P2P Transfers
Supports transferring funds within application

## Send funds from one account to another

**Request**:

`POST` `/users/:user_id/deposits`

Parameters:

Name       | Type   | Required | Description
-----------|--------|----------|------------
amount     | float  | Yes      | amount to be transferred


*Note:*

- Authorization Protected

**Response**:

```json
Content-Type application/json
201 Created

{
    "success": true,
    "message": "success",
    "data": {
        "id": "4322a4c4-c2ba-49a7-862c-2d7ccd7aa7b0",
        "reference": "bea291b793d2d8d2c6d413a7",
        "status": "success",
        "amount": 10,
        "recipient_details": {
            "id": "b11d0649-0d4d-4dce-a9b7-25d837469a2d",
            "username": "asummer",
            "first_name": "",
            "last_name": ""
        },
        "sender_details": {
            "id": "e9d28e78-a5cd-4af9-a2a4-e6e05b22d9c3",
            "username": "tumise",
            "first_name": "",
            "last_name": ""
        },
        "new_balance": 4960,
        "created": "2021-06-08T08:55:54+0100"
    }
}
```

- If user attempts to make transfer to self

```json
Content-Type application/json
400 Bad Request

{
    "success": false,
    "message": "failed",
    "data": {
        "non_field_errors": [
            "cannot make a transfer to self"
        ]
    }
}
```