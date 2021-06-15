# Fund
Supports sending funds to account

## Fund an account

**Request**:

`POST` `/users/:user_id/deposits`

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
201 Created

{
    "date_created": "2021-06-10T17:13:21+0100",
    "reference": "CslHjCnn9UzM",
    "amount": 54000.0,
    "receiver": "welzatm"
}
```