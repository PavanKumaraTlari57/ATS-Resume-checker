from datetime import datetime, timezone
 
from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session
 
from app.core.security import hash_session_token
from app.db.dependencies import get_db
from app.models.session import Session as UserSession
from app.models.user import User
 
 
def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
 
 
def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated"
    )
 
 
def get_current_session(
    session_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db)
) -> UserSession:
    # The parameter name must match the cookie key set in /auth/login.
    if not session_token:
        raise _unauthorized()
 
    token_hash = hash_session_token(session_token)
 
    user_session = (
        db.query(UserSession)
        .filter(
            UserSession.session_token_hash == token_hash,
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > utc_now()
        )
        .first()
    )
 
    if not user_session:
        raise _unauthorized()
 
    return user_session
 
 
def get_current_user(
    user_session: UserSession = Depends(get_current_session),
    db: Session = Depends(get_db)
) -> User:
    user = db.get(User, user_session.user_id)
 
    if not user or user.is_deleted:
        raise _unauthorized()
 
    return user