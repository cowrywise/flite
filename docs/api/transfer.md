# Transfer
Supports transfer of funds (P2P)

## Transfer from account

**Request**:

`POST` `account/:sender_balance_id>/transfer/:receiver_balance_id>/`

Parameters:

Name       | Type   | Required | Description
-----------|--------|----------|------------
date created   | date | No      | Date created.
reference   | string | No     | reference for process
amount | int | Yes       | Amount to be deposited.
receiver  | int | yes       | Receiver of transfer 
sender  | int | yes       | Owner 
status      | string | No       | status of funding
transfer type| string | Yes| transfer type(Card or P2P)

*Note:*

- Authorization Protected

**Response**:

```json
Content-Type application/json
200 OK

{
    "date_created": "2021-06-11T11:39:29+0100",
    "reference": "He9D39j2NaPn",
    "amount": 50000.0,
    "receiver": "welzatm",
    "status": "SUCCESS"
}
```

**Withdrawal Error**:
When the amount to be transfered is greater than current wallet balance.

```json
Content-Type application/json
406 NOT ACCEPTABLE

{
    "error": "You cant transfer than your available balance"
}
```
