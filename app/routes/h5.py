from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.h5_challenge import H5Challenge
from app.models.user import User

router = APIRouter(
    prefix="/api/challenges/h5",
    tags=["H5 Challenge"],
)


@router.get("/")
def get_h5_flag(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    challenge = (
        db.query(H5Challenge)
        .filter(H5Challenge.user_id == current_user.id)
        .first()
    )

    if challenge is None or not challenge.completed:
        raise HTTPException(
            status_code=403,
            detail="Challenge not completed",
        )

    return {
        "challenge": "H5",
        "flag": challenge.flag,
    }
