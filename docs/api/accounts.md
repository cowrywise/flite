# Accounts
Supports depositing, withdrawing, transferring, and viewing single and multiple transactions.

*Note:*

- All endpoints can only be accessed by the Users who own the account


## Make a deposit to a User's Account


**Request**:

`POST` `/users/:user_id/deposits`

Parameters:

Name       | Type   | Required | Description
-----------|--------|----------|------------
reference  | string | No       | Reference (reason) for deposit
amount     | float  | Yes      | Amount to deposit to User account


*Note:*

- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
201 CREATED

{
  "id": "25a4cf13-98bb-4a1d-8391-30463d8d0a3e",
  "owner": "d674ad04-79eb-4304-9e26-2b67d8b972d2",
  "reference": "Birthday Gift",
  "status": "SUCCESS",
  "amount": 50000.00,
  "new_balance": 23300.00
}
```

## Make a withdrawal from a User's Account

**Request**:

`POST` `/users/:user_id/withdrawals`

Parameters:

Name       | Type   | Required | Description
-----------|--------|----------|------------
reference  | string | No       | Reference (reason) for withdrawal.
amount     | float  | Yes      | Amount withdraw from User account.


*Note:*

- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
201 CREATED

{
  "id": "25a4cf13-98bb-4a1d-8391-30463d8d0a3e",
  "owner": "d674ad04-79eb-4304-9e26-2b67d8b972d2",
  "reference": "Birthday Gift",
  "status": "SUCCESS",
  "amount": 50000.00,
  "new_balance": 23300.00
}
```

## Make a Peer To Peer Transfer

**Request**:

`POST` `/account/:sender_account_id/transfers/:recipient_account_id`

Parameters:

Name       | Type   | Required | Description
-----------|--------|----------|------------
reference  | string | No       | Reference (reason) for transfer.
amount     | float  | Yes      | Amount to transfer to account.


*Note:*

- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
201 CREATED

{
  "id": "25a4cf13-98bb-4a1d-8391-30463d8d0a3e",
  "owner": "d674ad04-79eb-4304-9e26-2b67d8b972d2",
  "reference": "Birthday Gift",
  "status": "SUCCESS",
  "amount": 50000.00,
  "new_balance": 23300.00,
  "sender": "0f71ff7b-52ba-4729-8c35-e2a8ee9eec6d",
  "recipient": "b03fe233-6f71-429a-8c33-b9be5070823e"
}
```

## Fetch all Transactions from a User account

**Request**:

`GET` `/account/:account_id/transactions`

Parameters:


*Note:*

- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
200 OK

[
    {
    "id": "25a4cf13-98bb-4a1d-8391-30463d8d0a3e",
    "owner": "d674ad04-79eb-4304-9e26-2b67d8b972d2",
    "reference": "Birthday Gift.",
    "status": "SUCCESS",
    "amount": 50000.00,
    "new_balance": 23300.00
    },
    {
    "id": "55205984-499a-418b-9ce6-45e870c6d3ae", 
    "owner": "b25b3648-d4d7-46a6-a4e1-b325c77d77f8", 
    "reference": "Birthday Gift.", 
    "status": "SUCCESS", 
    "amount": 245369.86, 
    "new_balance": 30.
    }
]
```

## Fetch a single transaction from a User's account

**Request**:

`GET` `/account/:account_id/transactions/:transaction_id`

Parameters:


*Note:*

- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
200 OK

{
  "id": "25a4cf13-98bb-4a1d-8391-30463d8d0a3e",
  "owner": "d674ad04-79eb-4304-9e26-2b67d8b972d2",
  "reference": "Birthday Gift",
  "status": "SUCCESS",
  "amount": 50000.00,
  "new_balance": 23300.00
}
```