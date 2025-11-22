from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List

from app.services.user_service import CSVUserService
from app.deps import get_user_service, pwd_context, create_access_token, get_current_user
from app.schemas.user import UserCreate, UserOut, Token, UserUpdate

router = APIRouter(prefix="/auth", tags=["auth4"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: UserCreate,
    svc: CSVUserService = Depends(get_user_service),
):
    try:
        user = svc.create_user(
            username=payload.username,
            email=payload.email,
            password_hash=pwd_context.hash(payload.password),
            is_admin=False,
        )
        return UserOut(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            is_admin=user["is_admin"],
        )
    except ValueError as e:
        msg = str(e)
        if msg in {"username_taken", "email_taken"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg,
            )
        raise


@router.post("/token", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    svc: CSVUserService = Depends(get_user_service),
):
    user = svc.get_by_username(form.username)
    if not user or not pwd_context.verify(form.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_credentials",
        )

    token = create_access_token(
        username=user["username"],
        user_id=user["id"],
        is_admin=user["is_admin"],
        minutes=60,
    )
    return Token(access_token=token, token_type="bearer")


@router.get("/me", response_model=UserOut)
def me(curr=Depends(get_current_user)):
    return UserOut(
        id=curr["id"],
        username=curr["username"],
        email=curr["email"],
        is_admin=curr.get("is_admin", False),
    )


def get_current_admin(curr=Depends(get_current_user)):
    if not curr.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return curr


@router.get("/users", response_model=List[UserOut])
def list_users(
    _: dict = Depends(get_current_admin),
    svc: CSVUserService = Depends(get_user_service),
):
    users = svc.get_all_users()
    return [
        UserOut(
            id=u["id"],
            username=u["username"],
            email=u["email"],
            is_admin=u["is_admin"],
        )
        for u in users
    ]


@router.delete("/users/{user_id}")
def delete_user_route(
    user_id: int,
    _: dict = Depends(get_current_admin),
    svc: CSVUserService = Depends(get_user_service),
):
    ok = svc.delete_user(user_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user_not_found",
        )
    return {"status": "deleted"}

@router.put("/me", response_model=UserOut)
def update_me(
    payload: UserUpdate,
    curr=Depends(get_current_user),
    svc: CSVUserService = Depends(get_user_service),
):
    update_kwargs: dict = {}

    if payload.username is not None:
        update_kwargs["username"] = payload.username
    if payload.email is not None:
        update_kwargs["email"] = payload.email
    if payload.password is not None:
        update_kwargs["password_hash"] = pwd_context.hash(payload.password)

    if not update_kwargs:
        return UserOut(
            id=curr["id"],
            username=curr["username"],
            email=curr["email"],
            is_admin=curr.get("is_admin", False),
        )

    try:
        updated = svc.update_user(
            user_id=curr["id"],
            **update_kwargs,
        )
    except ValueError as e:
        msg = str(e)
        if msg in {"username_taken", "email_taken"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg,
            )
        if msg == "user_not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=msg,
            )
        raise

    return UserOut(
        id=updated["id"],
        username=updated["username"],
        email=updated["email"],
        is_admin=updated.get("is_admin", False),
    )

