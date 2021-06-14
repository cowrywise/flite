# Flite

# Setup
Note: Make sure you have docker and docker-compose installed.

Run instruction in terminal
1. Clone repo using `git clone <repo_url>`
2. cd into flite `cd flite`
3. start docker application `docker-compose up --build`
4. To run test
    * open another terminal whiles terminal of step #3 is running and get into docker environment (i.e. `docker exec -it  <container_id> bash`, you can get container_id via `docker ps`)
    * run `python manage.py test`