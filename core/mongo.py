from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from pymongo.database import Database
from model.schemas import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class MongoDatabaseHandler:
    instance = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(*args, **kwargs)
        return cls.instance

    def __init__(self):
        self.client = AsyncIOMotorClient()
        self.database = self.client['instagram']

    # Define a method to return the database object asynchronize
    async def get_database(self) -> Database:
        return self.database


# Create an instance of the database handler class
client = MongoDatabaseHandler()

# Get the 'users' collection from the database
db = client.database
users_collection = db.users


# Define an async function to create a new user in the database
async def create_user(user: User):
    hashed_password = pwd_context.hash(user.password)
    user.password = hashed_password
    result = await users_collection.insert_one(user.dict())
    return result.inserted_id


# Define an async function to retrieve a user from the database by username
async def get_user(username: str):
    user = await users_collection.find_one({"username": username})
    return user


# Define an async function to hash a plaintext password using bcrypt
async def get_password_hash(password: str):
    return pwd_context.hash(password)


# Define an async function to verify a plaintext password against a hashed password using bcrypt
async def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
