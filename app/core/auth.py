from typing import Optional, MutableMapping, List, Union
from datetime import datetime, timedelta

from fastapi import Request, HTTPException
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.orm.session import Session
from jose import jwt

from app.models.user import User
from app.shared.config import cfg
from app.core.security import verify_password


JWTPayloadMapping = MutableMapping[
    str, Union[datetime, bool, str, List[str], List[int]]
]


class OAuth2PasswordBearerCookie(OAuth2):
    def __init__(
        self,
        token_url: str,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": token_url, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=401,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None

        return param


oauth2_scheme = OAuth2PasswordBearerCookie(token_url=f"{cfg.API_V1_STR}/auth/login")


def authenticate(*, email: str, password: str, session: Session) -> Optional[User]:
    """
    Authenticate the user with the email and password provided

    Args:
        email (str): The email of the user to be authenticated.
        password (str): The password of the user to be authenticated.
        session (Session): A SQLAlchemy Session object that is connected to the database.

    Returns:
        Optional[User]: The authenticated user.
    """
    user = session.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        return None

    return user


def create_access_token(
    *, sub: str, lifetime: int = cfg.ACCESS_TOKEN_EXPIRE_MINUTES
) -> str:
    """
    Create a JWT access token with a `lifetime` expiry time.

    Args:
        sub (str): The data being stored in the token.
        lifetime (int, optional): The number of minutes for the newly created token will be alive. Defaults to cfg.ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        str: A new JWT.
    """
    return _create_token(
        token_type="access_token",
        lifetime=timedelta(minutes=lifetime),
        sub=sub,
    )


def _create_token(token_type: str, lifetime: timedelta, sub: str) -> str:
    """
    Helper function to create a JWT.

    Args:
        token_type (str): The type of token this is.
        lifetime (timedelta): The time in minutes for this token to expire.
        sub (str): The subject data of the token.

    Returns:
        str: A new JWT with specified info.
    """
    payload = {}
    expire = datetime.utcnow() + lifetime
    payload["type"] = token_type

    # https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.3
    # The "exp" (expiration time) claim identifies the expiration time on
    # or after which the JWT MUST NOT be accepted for processing
    payload["exp"] = expire

    # The "iat" (issued at) claim identifies the time at which the
    # JWT was issued.
    payload["iat"] = datetime.utcnow()

    # The "sub" (subject) claim identifies the principal that is the
    # subject of the JWT
    payload["sub"] = str(sub)
    return jwt.encode(payload, cfg.JWT_SECRET, algorithm=cfg.ALGORITHM)
