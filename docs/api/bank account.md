# Bank Account
Supports creating of bank account

## Create a bank account

**Request**:

`POST` `/bank/`

Parameters:

Name       | Type   | Required | Description
-----------|--------|----------|------------
account_name   | string | Yes      | Bank name
account_number   | string | Yes      | Bank number
bank | string | No       | bank id
owner | string | No       | user id

*Note:*

- Authorization Protected

**Response**:

```json
Content-Type application/json
201 Created

{
    "account_name": "Solesi Atilayo Temil",
    "account_number": "2023065759",
    "owner": "welzatm",
    "bank": "e34c742d-6a8e-476f-893b-d66b1827815f"
}
```
