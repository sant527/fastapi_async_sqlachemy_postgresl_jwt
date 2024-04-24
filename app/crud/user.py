from app.models import User as UserDBModel
from fastapi import HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate
from app.utils.auth import verify_password
from app.config import settings
from jose import JWTError, jwt
from app.api.dependencies.core import DBSessionDep
from typing import Annotated
from app.models import User

async def get_user(db_session: AsyncSession, user_id: int):
    user = (await db_session.scalars(select(UserDBModel).where(UserDBModel.id == user_id))).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_user_by_email(db_session: AsyncSession, email: str):
    return (await db_session.scalars(select(UserDBModel).where(UserDBModel.email == email))).first()

async def create_user(db_session: AsyncSession, user:UserCreate):
    db_user = UserDBModel(**user.dict())
    db_session.add(db_user)
    await db_session.commit()
    await db_session.refresh(db_user)
    return db_user

async def authenticate_user(db_session: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db_session, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


