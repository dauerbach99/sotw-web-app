from datetime import datetime
from typing import Dict

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session

from app import crud
from app import schemas
from app.api import deps

# from app.clients.email import EmailClient
# from app.core.email import send_registration_confirmed_email
from app.clients.spotify import SpotifyClient
from app.core.auth import authenticate
from app.core.auth import create_access_token
from app.models.user import User
from app.shared.config import cfg


router = APIRouter()


@router.post("/login", response_model=schemas.User)
async def login(
    session: Session = Depends(deps.get_session),
    *,
    form_data: OAuth2PasswordRequestForm = Depends(),
    response: Response,
) -> schemas.User:
    """
    Log the user in using the JWT for a user from OAuth2 request body.

    Args:
        response (Response): The response to be sent with the user that contains the cookie with the JWT.
        session (Session, optional): A SQLAlchemy Session object that is connected to the database. Defaults to Depends(deps.get_session).
        form_data (OAuth2PasswordRequestForm, optional): The username and password used to log in. Defaults to Depends().

    Raises:
        HTTPException: 400 when the app fails to authenticate the user based on the credentials given.

    Returns:
        schemas.User: The user object found after authentication.
    """
    user = authenticate(
        email=form_data.username, password=form_data.password, session=session
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password.")

    token = create_access_token(sub=user.id, lifetime=cfg.ACCESS_TOKEN_EXPIRE_MINUTES)

    response.set_cookie(
        "Authorization",
        value=f"Bearer {token}",
        httponly=True,
        max_age=cfg.SESSION_COOKIE_EXPIRE_SECONDS,
        expires=cfg.SESSION_COOKIE_EXPIRE_SECONDS,
        samesite="Lax",
        secure=False,
    )

    return user


@router.get("/logout")
async def logout(*, response: Response) -> Dict:
    """
    Delete the user's Authorization cookie for logout.

    Args:
        response (Response): The response to be sent with the user that contains no authorization cookie.

    Returns:
        Dict: A 200 response.
    """
    response.delete_cookie("Authorization")
    return {"status": 200}


@router.get("/current_user", response_model=schemas.User)
async def get_current_user(
    current_user: User = Depends(deps.get_current_user),
) -> schemas.User:
    """
    Fetch the currently logged in user.

    Args:
        current_user (User, optional): A dependency to get the authenticated user. Defaults to Depends(deps.get_current_user).

    Returns:
        schemas.User: The currently logged in user
    """

    return current_user


@router.post("/register", response_model=schemas.User, status_code=201)
async def register(
    session: Session = Depends(deps.get_session),
    *,
    # email_client: EmailClient = Depends(deps.get_email_client),
    # background_tasks: BackgroundTasks,
    user_in: schemas.UserCreate,
    response: Response,
) -> schemas.User:
    """
    Register a new user.

    Args:
        user_in (schemas.UserCreate): The payload with the new user's information.
        response (Response): The response to be sent with the new user that contains the cookie with the JWT.
        session (Session, optional): A SQLAlchemy Session object that is connected to the database. Defaults to Depends(deps.get_session).

    Raises:
        HTTPException: 400 when the user_in.email already exists in the database for another user.

    Returns:
        User: The newly created user
    """
    user = crud.user.get_by_email(session=session, email=user_in.email)

    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists.",
        )
    user = crud.user.create(session=session, object_in=user_in)

    # if cfg.SEND_REGISTRATION_EMAILS:
    #     background_tasks.add_task(send_registration_confirmed_email, user=user, client=email_client)

    # WIP give the user an access token upon registering
    # TODO: Have email verification link be used for login (spotify account linking redirects to email verification page -> loginregistration modal)
    token = create_access_token(sub=user.id, lifetime=cfg.ACCESS_TOKEN_EXPIRE_MINUTES)

    response.set_cookie(
        "Authorization",
        value=f"Bearer {token}",
        httponly=True,
        max_age=cfg.SESSION_COOKIE_EXPIRE_SECONDS,
        expires=cfg.SESSION_COOKIE_EXPIRE_SECONDS,
        samesite="Lax",
        secure=False,
    )

    return user


@router.get("/spotify-client-id")
async def spotify_client_id() -> Dict:
    """
    Retrieve the client ID for the spotify API

    Returns:
        Dict: A dictionary with the app's Spotify client ID
    """

    return {"status": 200, "client_id": cfg.SPOTIFY_CLIENT_ID}


@router.put("/spotify-access-token", response_model=schemas.User, status_code=202)
async def spotify_access_token(
    session: Session = Depends(deps.get_session),
    *,
    current_user: User = Depends(deps.get_current_user),
    spotify_client: SpotifyClient = Depends(deps.get_spotify_client),
    payload: schemas.UserSpotifyAuth,
) -> schemas.User:
    """
    Endpoint to link a user's spotify to the db by getting a new access token and the user's profile info

    Args:
        payload (schemas.UserSpotifyAuth): A payload with the authorization code for spotify for the user.
        session (Session, optional): A SQLAlchemy Session object that is connected to the database. Defaults to Depends(deps.get_session).
        current_user (User, optional): The currently logged in user making the request. Defaults to Depends(deps.get_current_user).
        spotify_client (SpotifyClient, optional): Client for Spotify interactions. Defaults to Depends(deps.get_spotify_client).

    Raises:
        HTTPException: 401 if the request body state does not match the current user's info

    Returns:
        schemas.User: 202 upon a successful update of the user.
    """

    if (
        not payload.state
        or current_user.email + "-" + current_user.name != payload.state
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized request.",
        )

    if payload.code:
        access_token, refresh_token, spotify_user_id = (
            spotify_client.get_access_refresh_tokens(payload.code)
        )
        object_in = schemas.UserUpdate(
            spotify_linked=True,
            spotify_access_token=access_token,
            spotify_refresh_token=refresh_token,
            spotify_user_id=spotify_user_id,
            spotify_accessed_date=datetime.utcnow(),
        )

        return crud.user.update(
            session=session, db_object=current_user, object_in=object_in
        )

    return current_user
