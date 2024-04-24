from pydantic import BaseModel, Field, EmailStr, ConfigDict

class UserCreate(BaseModel):
	email: EmailStr
	first_name: str
	last_name: str
	hashed_password: str = Field(alias="password")

class UserResponse(BaseModel):
	email: EmailStr
	first_name: str
	last_name: str
	id: int
	disabled: bool
	model_config = ConfigDict(from_attributes=True)