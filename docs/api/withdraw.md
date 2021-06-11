# Withdraw
Supports withdraw of funds

## Withdraw from account

**Request**:

`POST` `api/v1/user/:user_id/withdrawals/`

Parameters:

Name       | Type   | Required | Description
-----------|--------|----------|------------
date created   | date | No      | Date created.
reference   | string | No     | reference for process
amount | int | Yes       | Amount to be deposited.
receiver  | int | yes       | Owner 
status      | string | No       | status of funding

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
When the amount to be withdrawn is greater than account balance.

```json
Content-Type application/json
406 NOT ACCEPTABLE

{
    "error": "Check amount entered"
}
```
