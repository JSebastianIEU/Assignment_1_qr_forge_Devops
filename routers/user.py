from fastapi import APIRouter, Depends

from core.security import get_current_user
from models import User
from schemas import UserRead

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user
