from fastapi import APIRouter, status, HTTPException, Depends
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import Token
from app.api.dependencies.core import DBSessionDep
from app.utils.auth import hash_pass, create_refresh_token, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from app.config import settings
from typing import Annotated
from app.models import User
from app.crud.user import get_user_by_email, create_user, authenticate_user
from app.api.dependencies.auth import validate_is_authenticated

router = APIRouter(
	    prefix="/api/users",
	    tags=["users"],
        responses={404: {"description": "Not found"}},
	)

@router.post('/signup', summary="Create new user", status_code=status.HTTP_201_CREATED,response_model=UserResponse)
async def create_users(user_payload:UserCreate,db_session: DBSessionDep):
    # querying database to check if user already exist
    user = await get_user_by_email(email=user_payload.email,db_session=db_session)
    if user is not None:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist"
        )

    # Hash The Password
    user_payload.hashed_password = hash_pass(user_payload.hashed_password)

    new_user = await create_user(db_session=db_session, user=user_payload)
    return new_user

@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: DBSessionDep
):
    user = await authenticate_user(db_session=db_session,email=form_data.username,password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.get("/me", summary="Get Active User Details", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(validate_is_authenticated)]
):
    return current_user


# @router.get(
#     "/{user_id}",
#     response_model=User,
#     dependencies=[Depends(validate_is_authenticated)],
# )
# async def user_details(
#     user_id: int,
#     db_session: DBSessionDep,
# ):
#     """
#     Get any user details
#     """
#     user = await get_user(db_session, user_id)
#     return user