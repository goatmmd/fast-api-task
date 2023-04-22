from jose import jwt, ExpiredSignatureError
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from core.settings import JWT_CONFIG

from core.mongo import create_user, db
from model.schemas import User, Token
from utils.crawl import login_into_instagram, get_followers_list
from utils.jwt import create_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()


# Define an endpoint to list all users
@router.get("/users/", tags=["users"])
async def read_users():
    list_users = list()
    async for user in db.users.find():
        list_users.append(user['username'])

    return list_users


# Define an endpoint to create a new user
@router.post("/users/create/{username}/{password}", tags=["users"])
async def create_user_for_ig(username: str, password: str):
    result = await db.users.insert_one({'username': username, 'password': password})
    return {"_id": str(result.inserted_id)}


# Define an endpoint to log in to Instagram
@router.get('/users/ig/login/{username}', tags=['Instagram'])
async def login_ig(username: str):
    account = await db.users.find_one({'username': username})
    if not account:
        return HTTPException(status_code=404, detail='User not found.')

    result = login_into_instagram(account['username'], account['password'])
    if result[0]:
        user = {'user': {'username': account['username'], 'password': account['password']}}
        data = {**result[-1], **user}
        _id = await db.cookies.insert_one(data)
        return {'id': str(_id.inserted_id)}
    return HTTPException(status_code=400, detail='Account got an error')


# Define an endpoint to get the followers of an Instagram account
@router.get('/users/ig/followers/{username}', tags=['Instagram'])
async def get_followers(username: str):
    cookies = await db.cookies.find_one({'user.username': username})
    if not cookies:
        return HTTPException(status_code=404, detail='User not found.')

    result = get_followers_list(cookies)
    if result:
        return {'data': {'account': username, 'followers_count': len(result)}, 'followers': result}


# Define a protected endpoint to register a new user
@router.post("/register", tags=['protected'])
async def register_user(user: User):
    if await db.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Email already registered")
    await create_user(user)
    access_token = create_access_token(user.username)
    return Token(access_token=access_token, token_type="bearer")


# Define a protected endpoint that requires a valid access token
@router.get("/protected", tags=['protected'])
async def protected_endpoint(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_CONFIG['SECRET_KEY'], algorithms=JWT_CONFIG['ALGORITHM'])
        username = payload["sub"]
        return {'username': username}
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except:
        raise HTTPException(status_code=401, detail="Token is invalid")
