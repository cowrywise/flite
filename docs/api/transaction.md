# Transaction
Supports retrieval of transactions

## Fetch single transaction

**Request**:

`GET` `account/:balance_id/transactions/:transaction_id/`

Parameters:

Name       | Type   | Required | Description
-----------|--------|----------|------------
date created   | date | Yes      | Date created.
reference   | string | Yes     | reference for process
amount | int | Yes       | Amount to be deposited.
owner  | int | yes       | Owner 
status      | string | Yes       | status of funding
transfer type| string | Yes| transfer type(Card or P2P)
balance | int | Yes | balance id

*Note:*

- Authorization Protected

**Response**:

```json
Content-Type application/json
200 OK

{
    "id": "d34238f7-b8e8-487c-9338-74209ee9d8c3",
    "created": "2021-06-09T16:28:01.952Z",
    "modified": "2021-06-09T16:28:01.954Z",
    "owner_id": "542dbfb3-9e02-4956-99c3-28ae1d654474",
    "amount": 3000.0,
    "date_created": "2021-06-09T16:28:01.952Z",
    "reference": "NcKZpcbt6IzH",
    "status": "SUCCESS",
    "transaction_type": "Transfer(P2P)",
    "balance_id": "26fd7894-7707-4681-b965-b2901ca8ddce"
}
```

## Fetch all transactions of single account

**Request**:

`GET` `account/:balance_id/transaction/`

Parameters:

Name       | Type   | Required | Description
-----------|--------|----------|------------
id | string | Yes       | Transaction id

*Note:*

- Authorization Protected

**Response**:

```json
Content-Type application/json
200 OK

{
        "id": "9769847e-5745-48de-a8f6-19ca3b9c2d54",
        "created": "2021-06-11T10:47:57.034Z",
        "modified": "2021-06-11T10:47:57.035Z",
        "owner_id": "542dbfb3-9e02-4956-99c3-28ae1d654474",
        "amount": 450000.0,
        "date_created": "2021-06-11T10:47:57.035Z",
        "reference": "gHTsmjza26vW",
        "status": "FAILED",
        "transaction_type": "Withdraw",
        "balance_id": "26fd7894-7707-4681-b965-b2901ca8ddce"
    },
    {
        "id": "f6efa14f-2a0a-4aa2-9562-36bf7e3410c7",
        "created": "2021-06-11T10:41:36.494Z",
        "modified": "2021-06-11T10:41:36.495Z",
        "owner_id": "542dbfb3-9e02-4956-99c3-28ae1d654474",
        "amount": 450000.0,
        "date_created": "2021-06-11T10:41:36.495Z",
        "reference": "djgDap5GkWkB",
        "status": "FAILED",
        "transaction_type": "Withdraw",
        "balance_id": "26fd7894-7707-4681-b965-b2901ca8ddce"
    },
    {
        "id": "5e525535-53cf-44ae-98f7-5871164578ba",
        "created": "2021-06-11T10:39:30.094Z",
        "modified": "2021-06-11T10:39:30.094Z",
        "owner_id": "542dbfb3-9e02-4956-99c3-28ae1d654474",
        "amount": 50000.0,
        "date_created": "2021-06-11T10:39:30.094Z",
        "reference": "He9D39j2NaPn",
        "status": "SUCCESS",
        "transaction_type": "Withdraw",
        "balance_id": "26fd7894-7707-4681-b965-b2901ca8ddce"
    },
    {
        "id": "21818f7b-ca30-428d-9e67-394f09129010",
        "created": "2021-06-10T16:13:21.601Z",
        "modified": "2021-06-10T16:13:21.602Z",
        "owner_id": "542dbfb3-9e02-4956-99c3-28ae1d654474",
        "amount": 54000.0,
        "date_created": "2021-06-10T16:13:21.602Z",
        "reference": "CslHjCnn9UzM",
        "status": "SUCCESS",
        "transaction_type": "Fund Account",
        "balance_id": "26fd7894-7707-4681-b965-b2901ca8ddce"
    },
    {
        "id": "5d1509c4-68e5-4521-b3ac-320c67ac0f3f",
        "created": "2021-06-10T16:13:19.841Z",
        "modified": "2021-06-10T16:13:21.408Z",
        "owner_id": "542dbfb3-9e02-4956-99c3-28ae1d654474",
        "amount": 54000.0,
        "date_created": "2021-06-10T16:13:19.842Z",
        "reference": "CslHjCnn9UzM",
        "status": "FAILED",
        "transaction_type": "Fund Account",
        "balance_id": "26fd7894-7707-4681-b965-b2901ca8ddce"
    },
    {
        "id": "f583c567-2978-449f-8611-455901553ec3",
        "created": "2021-06-10T15:55:04.285Z",
        "modified": "2021-06-10T15:55:04.286Z",
        "owner_id": "542dbfb3-9e02-4956-99c3-28ae1d654474",
        "amount": 50000.0,
        "date_created": "2021-06-10T15:55:04.286Z",
        "reference": "vLPjcanren11",
        "status": "SUCCESS",
        "transaction_type": "Fund Account",
        "balance_id": "26fd7894-7707-4681-b965-b2901ca8ddce"
    },
    {
        "id": "a054d356-823f-4503-a2f7-11d2650e4afd",
        "created": "2021-06-10T15:55:04.094Z",
        "modified": "2021-06-10T15:55:04.279Z",
        "owner_id": "542dbfb3-9e02-4956-99c3-28ae1d654474",
        "amount": 50000.0,
        "date_created": "2021-06-10T15:55:04.095Z",
        "reference": "vLPjcanren11",
        "status": "FAILED",
        "transaction_type": "Fund Account",
        "balance_id": "26fd7894-7707-4681-b965-b2901ca8ddce"
    },
    {
        "id": "dae31097-3586-4a50-b70b-1a33545c767c",
        "created": "2021-06-10T15:54:10.757Z",
        "modified": "2021-06-10T15:54:11.083Z",
        "owner_id": "542dbfb3-9e02-4956-99c3-28ae1d654474",
        "amount": 30000.0,
        "date_created": "2021-06-10T15:54:10.759Z",
        "reference": "Y6FpFO38LtpQ",
        "status": "SUCCESS",
        "transaction_type": "Transfer(P2P)",
        "balance_id": "26fd7894-7707-4681-b965-b2901ca8ddce"
    },
    {
        "id": "1b883723-2c90-4cd7-8d9e-5cea011f391c",
        "created": "2021-06-10T15:50:49.346Z",
        "modified": "2021-06-10T15:50:49.347Z",
        "owner_id": "542dbfb3-9e02-4956-99c3-28ae1d654474",
        "amount": 50000.0,
        "date_created": "2021-06-10T15:50:49.347Z",
        "reference": "oZYGVJyKBdWo",
        "status": "SUCCESS",
        "transaction_type": "Fund Account",
        "balance_id": "26fd7894-7707-4681-b965-b2901ca8ddce"
    },
    {
        "id": "619e6a98-3c82-4d76-8ff7-96c125bd9b83",
        "created": "2021-06-10T15:50:49.168Z",
        "modified": "2021-06-10T15:50:49.227Z",
        "owner_id": "542dbfb3-9e02-4956-99c3-28ae1d654474",
        "amount": 50000.0,
        "date_created": "2021-06-10T15:50:49.168Z",
        "reference": "oZYGVJyKBdWo",
        "status": "FAILED",
        "transaction_type": "Fund Account",
        "balance_id": "26fd7894-7707-4681-b965-b2901ca8ddce"
    },
    {
        "id": "ac621a87-5d60-4853-bba6-a68bacf01de9",
        "created": "2021-06-10T15:49:39.685Z",
        "modified": "2021-06-10T15:49:39.685Z",
        "owner_id": "542dbfb3-9e02-4956-99c3-28ae1d654474",
        "amount": 5000.0,
        "date_created": "2021-06-10T15:49:39.685Z",
        "reference": "MUOqkyCgsFqj",
        "status": "SUCCESS",
        "transaction_type": "Fund Account",
        "balance_id": "26fd7894-7707-4681-b965-b2901ca8ddce"
    },
    {
        "id": "41aa969e-b0dc-48cd-bade-0171c9bfd80b",
        "created": "2021-06-10T15:49:39.562Z",
        "modified": "2021-06-10T15:49:39.589Z",
        "owner_id": "542dbfb3-9e02-4956-99c3-28ae1d654474",
        "amount": 5000.0,
        "date_created": "2021-06-10T15:49:39.563Z",
        "reference": "MUOqkyCgsFqj",
        "status": "FAILED",
        "transaction_type": "Fund Account",
        "balance_id": "26fd7894-7707-4681-b965-b2901ca8ddce"
    },
    {
        "id": "30c117ab-dc7c-4d2f-a3de-679b9672bc64",
        "created": "2021-06-10T15:49:33.837Z",
        "modified": "2021-06-10T15:49:33.838Z",
        "owner_id": "542dbfb3-9e02-4956-99c3-28ae1d654474",
        "amount": 5000.0,
        "date_created": "2021-06-10T15:49:33.838Z",
        "reference": "QpqqR5c7DFz5",
        "status": "SUCCESS",
        "transaction_type": "Fund Account",
        "balance_id": "26fd7894-7707-4681-b965-b2901ca8ddce"
    },
```
