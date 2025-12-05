from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from app.services.user_service import CSVUserService
from app.repositories.csv_repository import CSVRepository

from app.services.readinglist_service import ReadingListService
from app.repositories.book_repository import BookRepository
from app.deps import get_user_service, pwd_context, create_access_token, get_current_user
from app.schemas.user import UserCreate, UserOut, Token, UserUpdate, PublicUserOut



router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description="Creates a new user with a unique username and email.",
    response_description="The newly created user.",
)
def register(payload: UserCreate, svc: CSVUserService = Depends(get_user_service)):
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
        if msg == "username_taken":
            friendly_msg = "Username is taken"
        elif msg == "email_taken":
            friendly_msg = "Email is taken"
        else:
            friendly_msg = msg
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=friendly_msg,
        )


@router.post(
    "/token",
    summary="Log in and obtain access token",
    description="Authenticates a user using username and password and returns a bearer token.",
    response_model=Token,
    response_description="Access token to be used in the Authorization header.",
)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    svc: CSVUserService = Depends(get_user_service),
):
    user = svc.get_by_username(form.username)
    if not user or not pwd_context.verify(form.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong username or password",
        )

    if user.get("is_suspended", False):
        raw_until = user.get("suspended_until") or "N/A"
        reason = user.get("suspension_reason") or "No suspension reason provided"

        try:
            dt = datetime.fromisoformat(raw_until)
            pretty_until = dt.strftime("%Y-%m-%d %H:%M")
        except:
            pretty_until = raw_until

        detail_message = (
            f"Your account is suspended until {pretty_until}. "
            f"Suspension Reason: {reason}"
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail_message,
        )

    token = create_access_token(
        username=user["username"],
        user_id=user["id"],
        is_admin=user["is_admin"],
        minutes=60,
    )

    return Token(access_token=token, token_type="bearer")



@router.get(
    "/me",
    summary="Get current user profile",
    description="Returns the profile of the current authenticated user.",
    response_model=UserOut,
    response_description="The current user's profile.",
)
def me(curr=Depends(get_current_user)):
    return UserOut(
        id=curr["id"],
        username=curr["username"],
        email=curr["email"],
        is_admin=curr["is_admin"],
    )


@router.get(
    "/users",
    summary="List all users (Admin only)",
    description="Returns all registered users. Admin only.",
    response_model=List[UserOut],
    response_description="A list of users.",
)
def list_users(
    curr=Depends(get_current_user),
    svc: CSVUserService = Depends(get_user_service),
):
    if not curr.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    rows = svc.repo.read_all(svc.path)
    users_out = []

    for row in rows:
        user_id = int(row["id"])
        raw_flag = str(row.get("is_admin", "")).strip().lower()
        is_admin = raw_flag in {"true", "1", "yes"}

        users_out.append(
            UserOut(
                id=user_id,
                username=row["username"],
                email=row["email"],
                is_admin=is_admin,
            )
        )

    return users_out


@router.get(
    "/search",
    summary="Search users by username",
    description="Admin-only search for users whose username contains the query.",
)
def search_users(
    username: str,
    curr=Depends(get_current_user),
    svc: CSVUserService = Depends(get_user_service),
):
    if not curr.get("is_admin"):
        raise HTTPException(403, "Admin privileges required")

    username_norm = username.strip().lower()
    rows = svc.repo.read_all(svc.path)

    matched = []
    for row in rows:
        if username_norm in row["username"].lower():
            matched.append(
                {
                    "id": int(row["id"]),
                    "username": row["username"],
                    "email": row["email"],
                    "is_admin": str(row.get("is_admin", "false")).lower()
                    in {"true", "1", "yes"},
                    "is_suspended": str(row.get("is_suspended", "false")).lower()
                    in {"true", "1", "yes"},
                    "suspended_until": row.get("suspended_until") or None,
                    "suspension_reason": row.get("suspension_reason") or None,
                    "warnings": int(row.get("warnings") or 0),
                }
            )

    return matched


@router.post(
    "/suspend/{user_id}",
    summary="Suspend a user",
    description="Suspends a user account for a given number of minutes. Admin only.",
)
def suspend_user_route(
    user_id: int,
    duration_minutes: int = Query(..., ge=1),
    reason: str | None = Query(None),
    curr=Depends(get_current_user),
    svc: CSVUserService = Depends(get_user_service),
):
    if not curr.get("is_admin"):
        raise HTTPException(403, "Admin privileges required")

    try:
        suspended_user = svc.suspend_user(
            admin_id=curr["id"],
            target_id=user_id,
            duration_minutes=duration_minutes,
            reason=reason,
        )
        return {
            "message": f"User {user_id} suspended for {duration_minutes} minutes.",
            "suspended_until": suspended_user["suspended_until"],
            "suspension_reason": suspended_user.get("suspension_reason") or None,
        }
    except ValueError:
        raise HTTPException(404, "User not found")


@router.post(
    "/unsuspend/{user_id}",
    summary="Unsuspend a user",
    description="Removes suspension from a user account. Admin only.",
)
def unsuspend_user_route(
    user_id: int,
    curr=Depends(get_current_user),
    svc: CSVUserService = Depends(get_user_service),
):
    if not curr.get("is_admin"):
        raise HTTPException(403, "Admin privileges required")

    try:
        svc.unsuspend_user(curr["id"], user_id)
        return {"message": f"User {user_id} is no longer suspended."}
    except ValueError:
        raise HTTPException(404, "User not found")


@router.put(
    "/me",
    summary="Update current user profile",
    description="Updates the current authenticated user's profile information.",
    response_model=UserOut,
    response_description="The updated user profile.",
)
def update_me(
    payload: UserUpdate,
    curr=Depends(get_current_user),
    svc: CSVUserService = Depends(get_user_service),
):
    update_data = payload.dict(exclude_unset=True)

    username = update_data.get("username")
    email = update_data.get("email")

    is_admin = update_data.get("is_admin") if curr.get("is_admin") else None

    try:
        user = svc.update_user(
            user_id=curr["id"],
            username=username,
            email=email,
            is_admin=is_admin,
        )

        return UserOut(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            is_admin=user["is_admin"],
        )

    except ValueError as e:
        msg = str(e)

        if msg == "Username is taken":
            friendly_msg = "Username is taken"
            code = status.HTTP_400_BAD_REQUEST
        elif msg == "Email is taken":
            friendly_msg = "Email is taken"
            code = status.HTTP_400_BAD_REQUEST
        elif msg == "User not found":
            friendly_msg = "User not found"
            code = status.HTTP_404_NOT_FOUND
        else:
            friendly_msg = msg
            code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(
            status_code=code,
            detail=friendly_msg,
        )


@router.get("/suspended")
def list_suspended(
    curr=Depends(get_current_user),
    svc: CSVUserService = Depends(get_user_service),
):
    if not curr.get("is_admin"):
        raise HTTPException(403, "Admin privileges required")

    rows = svc.repo.read_all(svc.path)
    suspended = []

    for row in rows:
        is_suspended = (
            str(row.get("is_suspended", "false")).lower() in {"true", "1", "yes"}
        )

        if is_suspended:
            suspended.append(
                {
                    "id": int(row["id"]),
                    "username": row["username"],
                    "email": row["email"],
                    "is_suspended": is_suspended,
                    "suspended_until": row.get("suspended_until") or "N/A",
                    "suspension_reason": row.get("suspension_reason") or None,
                    "warnings": int(row.get("warnings") or 0),
                }
            )

    return suspended

@router.get(
    "/search-users",
    summary="Search for registered users",
    description="Search users and show their public reading lists.",
    response_model=List[PublicUserOut],
)
def search_registered_users(
    username: str = Query(...),
    curr = Depends(get_current_user),
    user_svc: CSVUserService = Depends(get_user_service),
    readinglist_service: ReadingListService = Depends(lambda: ReadingListService(
        repo=CSVRepository(),
        book_repo=BookRepository()
    )),
):
    if not curr:
        raise HTTPException(
            401, "You must be logged in to search users."
        )

    username_norm = username.strip().lower()

    # 1. Load users
    users = user_svc.repo.read_all(user_svc.path)

    # 2. Load reading lists from actual readinglist.csv
    readinglists = readinglist_service.repo.read_all("backend/app/data/readinglists.csv")

    # 3. Group lists by user
    lists_by_user = {}
    for rl in readinglists:
        user_id = rl["UserID"]
        if user_id not in lists_by_user:
            lists_by_user[user_id] = []
        lists_by_user[user_id].append(rl)

    results = []

    for user in users:
        if username_norm in user["username"].lower():

            uid = str(user["id"])
            user_lists = lists_by_user.get(uid, [])

            # Filter for public lists AND expand books
            structured_lists = []
            for item in user_lists:
                if str(item.get("IsPublic", "true")).lower() == "true":
                    structured_lists.append({
                        "name": item.get("Name", "My List"),
                        "books": item.get("ISBNs", "").split("|")
                    })

            results.append(
                PublicUserOut(
                    id=int(user["id"]),
                    username=user["username"],
                    reading_list=structured_lists
                )
            )

    return results

