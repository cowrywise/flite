# Flite

**PostMan Documentation link:**
https://documenter.getpostman.com/view/5673795/TzeRrB27

![image](https://user-images.githubusercontent.com/16105527/121635621-75719480-ca7e-11eb-8040-bf7876ae0483.png)

**To start project, sipmly run:**

docker-compose up

The Following assumptions was made:

**For Withdrawal:**
# TODO: Assumptions 
        # JWT Token Verification was successful 
        # Username in token matches draccount name
        # Device macthes any known device
        # Name enquiry for craccountno is successful
        # Verified requestid is unique by saving, cancel transaction if not
        # Verified token
        # Verified draccount has no PND
        # Verified transactions falls withing draccount limit
        
**For Transfer:**
# TODO: Assumptions
        # Verify JWT token
        # Verify username in token matches draccount name
        # Verify Device macthes any known device
        # Name enquiry for craccountno is successful
        # Verify requestid is unique by saving, cancel transaction if not
        # Verify token
        # Verify draccount has no PND
        # Verify transactions falls withing draccount limit
        
All Transaction saving multithreading so as to improve performance. 
        
