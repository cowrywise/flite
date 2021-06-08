# Transactions
Supports deposits, withdraw, transfer, transaction listing and single transaction fetching of a user.

## Deposit into an account

**Request**:

`POST` `/users/:user_id/deposits`

Parameters:

Name     | Type    | Required | Description
---------|---------|----------|------------
amount   | decimal | Yes      | The amount a user wants to deposit, it should be in 2 decimal places.

*Note:*

- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
200 OK

{
    "amount": "5000.00",
    "id": "101047fc-4c43-40e5-883e-ba00ced9c9c9",
    "owner": "bbf44ac7-97b8-4038-aa80-b765c545caff",
    "reference": "eej1fs7z",
    "status": "Successful",
    "transaction_type": "Deposit",
    "new_balance": "59600.00",
    "created": "2021-06-08T22:08:51+0100"
}
```


## Withdraw from an account

**Request**:

`POST` `/users/:user_id/withdrawals`

Parameters:

Name     | Type    | Required | Description
---------|---------|----------|------------
amount   | decimal | Yes      | The amount a user wants to withdraw, it should be in 2 decimal places.

*Note:*

- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
200 OK

{
    "amount": "1000.00",
    "id": "2b588232-9a5b-4830-a5f6-e05f3005c1bb",
    "owner": "bbf44ac7-97b8-4038-aa80-b765c545caff",
    "reference": "l498ucr1",
    "status": "Successful",
    "transaction_type": "Withdraw",
    "new_balance": "58600.00",
    "created": "2021-06-08T22:38:07+0100"
}
```


## PeerToPeer transfer from one account to another

**Request**:

`POST` `/account/:sender_account_id/transfers/:recipient_account_id`

Parameters:

Name     | Type    | Required | Description
---------|---------|----------|------------
amount   | decimal | Yes      | The amount a user wants to transfer, it should be in 2 decimal places.

*Note:*

- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
200 OK

{
    "amount": "500.00",
    "id": "c4727ed2-44a1-43ea-bdb5-32332b8af8e9",
    "owner": "bbf44ac7-97b8-4038-aa80-b765c545caff",
    "sender": "bbf44ac7-97b8-4038-aa80-b765c545caff",
    "recipient": "a09d27e8-870d-40e9-a544-70fce1a48eb9",
    "reference": "ksh2hwk2",
    "status": "Successful",
    "transaction_type": "Peer To Peer (Debit)",
    "new_balance": "58100.00",
    "created": "2021-06-08T22:50:39+0100"
}
```


## Paginated list of transactions for a given account

**Request**:

`GET` `/account/:account_id/transactions`

Parameters:


*Note:*

- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
200 OK

{
     "results": [
        {
            "amount": "500.00",
            "id": "c4727ed2-44a1-43ea-bdb5-32332b8af8e9",
            "owner": "bbf44ac7-97b8-4038-aa80-b765c545caff",
            "reference": "ksh2hwk2",
            "status": "Successful",
            "transaction_type": "Peer To Peer (Debit)",
            "new_balance": "58100.00",
            "created": "2021-06-08T22:50:39+0100"
        },
        {
            "amount": "1000.00",
            "id": "2b588232-9a5b-4830-a5f6-e05f3005c1bb",
            "owner": "bbf44ac7-97b8-4038-aa80-b765c545caff",
            "reference": "l498ucr1",
            "status": "Successful",
            "transaction_type": "Withdraw",
            "new_balance": "58600.00",
            "created": "2021-06-08T22:38:07+0100"
        },
        {
            "amount": "5000.00",
            "id": "101047fc-4c43-40e5-883e-ba00ced9c9c9",
            "owner": "bbf44ac7-97b8-4038-aa80-b765c545caff",
            "reference": "eej1fs7z",
            "status": "Successful",
            "transaction_type": "Deposit",
            "new_balance": "59600.00",
            "created": "2021-06-08T22:08:51+0100"
        }
    ],
    "count": 14,
    "next": "http://127.0.0.1:8009/api/v1/account/bbf44ac7-97b8-4038-aa80-b765c545caff/transactions/?page=2&limit=3",
    "previous": null
}
```


## Single transaction for a given account

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
    "amount": "500.00",
    "id": "c4727ed2-44a1-43ea-bdb5-32332b8af8e9",
    "owner": "bbf44ac7-97b8-4038-aa80-b765c545caff",
    "reference": "ksh2hwk2",
    "status": "Successful",
    "transaction_type": "Peer To Peer (Debit)",
    "new_balance": "58100.00",
    "created": "2021-06-08T22:50:39+0100"
}
```
