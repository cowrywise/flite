# Fund
Supports sending funds to account

## Fund an account

**Request**:

`POST` `/users/:user_id/deposits`

Parameters:

Name       | Type   | Required | Description
-----------|--------|----------|------------
amount | int | Yes       | The amount to be deposited.

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
