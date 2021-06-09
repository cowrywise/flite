# Accounts
for P2P Transfers, all transactions, Single Transaction

## P2P transfers

**Request**:

`POST` `/account/:sender_account_id/transfers/:recipient_account_id/`

Parameters:

Name       | Type   | Required | Description
-----------|--------|----------|------------
amount     | float  | Yes      | Amount to transfer.

**Response**:

```json
Content-Type application/json
200 Success
{
  "status": "success",
  "data": {
    "id": "18d9d10f-ca79-464d-903c-e709ff92458d",
    "sender": {
      "id": "a8f0cb87-4145-4e0d-b71c-c79cfaac35e1",
      "username": "el-joft",
      "first_name": "King",
      "last_name": ""
    },
    "receipient": {
      "id": "7ec88f5a-230b-4c0b-857d-b893e3fd13aa",
      "username": "vasilias",
      "first_name": "",
      "last_name": ""
    },
    "amount": 1000.0
  }
}
```


## Get a user's transaction information

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
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "130ff11e-04c8-4946-bdc5-20cdf7fee94f",
      "reference": "34343412332",
      "status": "DONE",
      "amount": 3000.0,
      "new_balance": 50000.0,
      "owner": {
        "id": "7ec88f5a-230b-4c0b-857d-b893e3fd13aa",
        "username": "vasilias",
        "first_name": "",
        "last_name": ""
      }
    },
    {
      "id": "32146088-1179-46e2-bad0-da0bb797c5e1",
      "reference": "ACCT/TRA/41b839d4",
      "status": "DONE",
      "amount": 1000.0,
      "new_balance": 1000.0,
      "owner": {
        "id": "7ec88f5a-230b-4c0b-857d-b893e3fd13aa",
        "username": "vasilias",
        "first_name": "",
        "last_name": ""
      }
    }
  ]
}
```


## Get User's Single Transaction

**Request**:

`GET` `/account/:account_id/transactions/:transaction_id`


*Note:*

- All parameters are optional
- **[Authorization Protected](authentication.md)**

**Response**:

```json
Content-Type application/json
200 OK

{
  "status": "success",
  "data": {
    "id": "9486b6d5-e299-44f3-89fe-cca9a983a2af",
    "reference": "2012-201-2012121",
    "status": "PENDING",
    "amount": 20000.0,
    "new_balance": 2000.0,
    "owner": {
      "id": "a8f0cb87-4145-4e0d-b71c-c79cfaac35e1",
      "username": "el-joft",
      "first_name": "King",
      "last_name": ""
    }
  }
}
```
