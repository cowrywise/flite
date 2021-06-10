# Flite

## Procedure
1. Run python manage.py makemigrations
2. Run python manage.py migrate
3. Run python manage.py populate_banks(This is to populate with all banks in Nigeria)

## Challenge
For funding of account, i tried using the paystack Charge API but then realised not all banks were supported for bank account payment.The best alternative will have been using the Kudabank API but was unable to register so could not get the public and private keys however the endpoint works but funding is from abstract source
