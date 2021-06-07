# Flite

# How To Run
```
    docker-compose up
```

# Assumptions Used in Implmenting Endpoints

## General Assumption
- All Transactions (withdrawl, deposit and p2ptransfer) ensure Transaction Atomicty to ensure rollbacks should incase any process fail during a withdrawal, deposit or transfer

## Withdrawls and Deposits

### Withdrwals
- when a user makes a withdrawl, a new balance record is entered on the balance Table
- A transaction with a signed amount is recorded against the User in the Transaction Table (e.g -2000 when user withdraws 2000)
- a reference id is generated and stored against the transaction record

### Deposits
- when a user makes a deposit, a new balance record is entered on the balance Table
- A transaction is recorded against the user on the Transaction Table
- a reference id is generated and stored against the transaction record

## P2pTransactions

- 3 Tables gets updated when a p2p transaction occurs: Balance, Transaction and p2pTransfer
- a reference id is first created 
- a new record is created against the sender account on the Balance Table 
- a new record is created against the recipient account on the Balance Table
- two transactions are created in the Transaction table with the same reference id (negative amount is recorded for sender - debit transaction, and positive for recipient - credit transaction)
- a p2pTransfer record is created on the P2P table with owner and sender fields set to the sender object and the reference id generated at the start of the process is also stored against this P2PTransfer Table record


# Endpoints Description

- Deposits
```
users/:user_id/deposits/ -> Endpoint for Making Deposits into a wallet by the wallet owner over a post request

sample payload:
 {
    amount': 40000
 }

 sample response:
 {
    "transaction_id": "18d1a83c-aa4f-40aa-9627-6adcd5c0541d",
    "amount": 40000.0,
    "transaction_type": "credit",
    "available_balance": 40000.0,
    "status": "completed",
    "reference": "601646",
    "created": "2021-06-07T14:19:03.478448Z",
    "updated": "2021-06-07T14:19:03.478886Z"
}
```

- Withdrawals
```
users/:user_id/withdrawals/ -> Endpoint for Making withdrawls from a wallet by the wallet owner over a post request

sample payload:
 {
    amount': 10000
 }

 sample response:
 {
    "transaction_id": "cb0f6ad0-bd56-4967-a2a7-67e265be0c34",
    "amount": 30000.0,
    "transaction_type": "debit",
    "available_balance": 30000.0,
    "status": "completed",
    "reference": "261452",
    "created": "2021-06-07T14:19:59.683161Z",
    "updated": "2021-06-07T14:19:59.683528Z"
}
```

- Transactions (List)
```
account/:account_id/transactions -> Returns a list of all transactions made by a user

sample response:
[
    {
        "id": "832ef2ae-d6d1-4ae3-99c7-7f5fa094c4f9",
        "created": "2021-06-07T12:48:24+0100",
        "modified": "2021-06-07T12:48:24+0100",
        "reference": "236853",
        "status": "completed",
        "amount": -1000.0,
        "new_balance": 9000.0,
        "owner": "e4c317b7-e1e0-4877-bf2d-63cf3a2c0f1c"
    },
    {
        "id": "2c33c548-2ecc-4a48-83a7-eb39cc49dcde",
        "created": "2021-06-07T12:48:24+0100",
        "modified": "2021-06-07T12:48:24+0100",
        "reference": "236853",
        "status": "completed",
        "amount": 1000.0,
        "new_balance": 9000.0,
        "owner": "e4c317b7-e1e0-4877-bf2d-63cf3a2c0f1c"
    }
]

```

- Transactions (Detail)
```
account/:account_id/transactions/transaction_id -> Returns a transaction made by it's id

sample response:
{
    "id": "2c33c548-2ecc-4a48-83a7-eb39cc49dcde",
    "created": "2021-06-07T12:48:24+0100",
    "modified": "2021-06-07T12:48:24+0100",
    "reference": "236853",
    "status": "completed",
    "amount": 1000.0,
    "new_balance": 9000.0,
    "owner": "e4c317b7-e1e0-4877-bf2d-63cf3a2c0f1c"
}

```

- p2pTransfer
```
account/:sender_account_id/transfers/:recipient_account_id/ -> sends money from sender account/ wallet to recipient account / wallet

sample payload:
{
    amount': 10000
 }

 sample response:
 {
    "id": "0ceda771-c0f0-4b9c-b8ab-bbecc0f7cbea",
    "created": "2021-06-07T15:43:22+0100",
    "modified": "2021-06-07T15:43:22+0100",
    "reference": "281932",
    "status": "completed",
    "amount": 10000.0,
    "new_balance": 20000.0,
    "owner": "e4c317b7-e1e0-4877-bf2d-63cf3a2c0f1c",
    "sender": "e4c317b7-e1e0-4877-bf2d-63cf3a2c0f1c",
    "receipient": "edb8a0a3-4855-43e2-9c60-bb4a3434c1f0"
}

```