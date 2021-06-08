# Flite
# Local Set Up

### Docker

- run ```docker-compose up```

### Manual SetUp

- clone the repository
- create a virtual environment and activate
- run ```pip install -r requirements.txt```
- run ```python manage.py makemigrations```
- run ```python manage.py migrate```
- run ```python manage.py runserver```

*Note:*

- **Local Db is sqlite3 but can be changed in flite/config**

### Assumptions

- No Transfer Charges and Stamp Duties
- Book Balance is Equals Available Balance
- Minimum Balance is Zero
- There is No Minimum Withdrawal Or Deposit
- When A withdrawal is made, account is debited i.e(No Withdrawal Service)
- When A Deposit is made, account is credited.

