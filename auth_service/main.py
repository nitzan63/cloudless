from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
import httpx
import os
from datetime import datetime, timedelta
from functools import partial

SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
DATA_SERVICE_URL = os.environ.get("DATA_SERVICE_URL", "http://localhost:8002")

app = FastAPI(title="Auth Service")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

security = HTTPBearer()

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    password: str
    type: str

class UserService:
    def __init__(self, base_url=DATA_SERVICE_URL):
        self.base_url = base_url

    async def register_user(self, username: str, password: str, user_type: str):
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}/users/register", json={"username": username, "password": password, "type": user_type})
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=resp.json().get("detail", "Registration failed"))
            return resp.json()

    async def authenticate_user(self, username: str, password: str):
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/users/{username}")
            if resp.status_code != 200:
                return False
            user = resp.json()
            # Verify password remotely
            # Instead, we can POST to a verify endpoint, but for now, fetch hash and check here
            import bcrypt
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return False
            return user

user_service = UserService()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(required_type: str = None, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token: no username")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    # Fetch user from data service
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{DATA_SERVICE_URL}/users/{username}")
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="User not found")
        user = resp.json()
    if required_type and user.get("type") != required_type:
        raise HTTPException(status_code=403, detail=f"User must be of type '{required_type}'")
    return user

def user_type_dependency(required_type):
    async def dependency(credentials: HTTPAuthorizationCredentials = Depends(security)):
        return await get_current_user(required_type, credentials)
    return dependency

@app.post("/register")
async def register(user: User):
    await user_service.register_user(user.username, user.password, user.type)
    return {"status": "success"}

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/protected-producer")
async def protected_producer_route(user=Depends(user_type_dependency("producer"))):
    return {"username": user['username']}


@app.get("/protected-submitter")
async def protected_submitter_route(user=Depends(user_type_dependency("submitter"))):
    return {"username": user['username']}
