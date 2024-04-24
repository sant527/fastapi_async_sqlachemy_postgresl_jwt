from app import models

from .user import CurrentUserDep


async def validate_is_authenticated(
    current_user: CurrentUserDep,
) -> models.User:
    """
    This just returns as the CurrentUserDep dependency already throws if there is an issue with the auth token.
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
