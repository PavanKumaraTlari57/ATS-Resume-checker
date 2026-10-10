import os

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.security import (
    generate_session_token,
    hash_password,
    hash_session_token,
    verify_password,
)

from app.core.current_user import get_current_session, get_current_user
from app.db.dependencies import get_db
from app.models.session import Session as UserSession
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


MAX_FAILED_LOGIN_ATTEMPTS = 5
LOCK_DURATION_MINUTES = 15
SESSION_DURATION_DAYS = 7
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        email_verified=False
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )

    db.refresh(user)

    return RegisterResponse(
        id=str(user.id),
        name=user.name,
        email=user.email,
        email_verified=user.email_verified
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK
)
def login(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    # Do not reveal whether the email exists.
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Deleted accounts cannot log in.
    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    now = utc_now()

    # Check temporary account lock.
    if user.locked_until and user.locked_until > now:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account is temporarily locked"
        )

    # If an old lock has ended, start fresh.
    if user.locked_until and user.locked_until <= now:
        user.failed_login_attempts = 0
        user.locked_until = None

    # Verify password.
    if not user.password_hash or not verify_password(
        data.password,
        user.password_hash
    ):
        user.failed_login_attempts += 1

        if user.failed_login_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
            user.locked_until = (
                now + timedelta(minutes=LOCK_DURATION_MINUTES)
            )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Successful login.
    user.failed_login_attempts = 0
    user.locked_until = None

    raw_session_token = generate_session_token()
    session_token_hash = hash_session_token(raw_session_token)

    expires_at = now + timedelta(days=SESSION_DURATION_DAYS)

    user_session = UserSession(
        user_id=user.id,
        session_token_hash=session_token_hash,
        created_at=now,
        expires_at=expires_at
    )

    db.add(user_session)
    db.commit()

    # HTTP-only cookie prevents JavaScript from reading the session token.
    response.set_cookie(
        key="session_token",
        value=raw_session_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        expires=expires_at.replace(tzinfo=timezone.utc)
    )

    return LoginResponse(
        id=str(user.id),
        name=user.name,
        email=user.email,
        email_verified=user.email_verified,
        expires_at=expires_at
    )

@router.get("/me", response_model=RegisterResponse)
def me(current_user: User = Depends(get_current_user)):
    return RegisterResponse(
        id=str(current_user.id),
        name=current_user.name,
        email=current_user.email,
        email_verified=current_user.email_verified
    )

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    user_session: UserSession = Depends(get_current_session),
    db: Session = Depends(get_db)
):
    user_session.revoked_at = utc_now()
    db.commit()
    response.delete_cookie(
        "session_token",
        secure=COOKIE_SECURE,
        httponly=True,
        samesite="lax"
    )