# fast-api-task
This project is my task for Daneshgostar Corporation

# Endpoints
### User(withour JWT):
    - /users/                                                        - List
    - /users/create/{username}/{password}                            - Create
### Instagram:
    - /users/ig/login/{username}                                     - Retrieve
    - /users/ig/followers/{username}                                 - List
### User(JWT):
    - /register                                                     - Create
    - /Protected 

### Docs:
   ## - User (without JWT): 
       - register users for logging in instagram
        - get list of users in db
   ## - Instagram 
        - login into ig by users that you have registred 
        - get list of follower by users that you have login with it once at least 
   ## - User (Jwt)
        - register user and retrive a temporary  access token
        - an  endpoit for testing your access token 
        
