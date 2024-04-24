from pydantic import BaseModel, Field, EmailStr, ConfigDict

class Token(BaseModel):
	access_token: str
	refresh_token: str
	token_type: str

class TokenData(BaseModel):
    email: EmailStr
    permissions: str = "user"