from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.follower import Follower
from ..models.post import Post
from ..models.user import User
from ..schemas.user import UserCreate, UserProfileResponse, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


def _enrich_user(db: Session, user: User) -> UserResponse:
    followers = db.query(Follower).filter(Follower.following_id == user.id).count()
    following = db.query(Follower).filter(Follower.follower_id == user.id).count()
    posts = db.query(Post).filter(Post.author_id == user.id).count()
    return UserResponse(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        bio=user.bio,
        profile_picture_url=user.profile_picture_url,
        is_recruiter=user.is_recruiter,
        is_verified=user.is_verified,
        followers_count=followers,
        following_count=following,
        posts_count=posts,
        created_at=user.created_at,
    )


@router.post("", response_model=UserResponse, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return _enrich_user(db, user)


@router.get("", response_model=list[UserResponse])
def list_users(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    users = db.query(User).order_by(User.id).limit(limit).all()
    return [_enrich_user(db, u) for u in users]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return _enrich_user(db, user)


@router.post("/{user_id}/follow/{target_id}", status_code=201)
def follow_user(user_id: int, target_id: int, db: Session = Depends(get_db)):
    if user_id == target_id:
        raise HTTPException(400, "Cannot follow yourself")
    existing = (
        db.query(Follower)
        .filter(Follower.follower_id == user_id, Follower.following_id == target_id)
        .first()
    )
    if existing:
        raise HTTPException(409, "Already following")
    db.add(Follower(follower_id=user_id, following_id=target_id))
    db.commit()
    return {"detail": "Followed"}


@router.delete("/{user_id}/follow/{target_id}")
def unfollow_user(user_id: int, target_id: int, db: Session = Depends(get_db)):
    rel = (
        db.query(Follower)
        .filter(Follower.follower_id == user_id, Follower.following_id == target_id)
        .first()
    )
    if not rel:
        raise HTTPException(404, "Not following")
    db.delete(rel)
    db.commit()
    return {"detail": "Unfollowed"}


@router.get("/{user_id}/followers", response_model=list[UserResponse])
def get_followers(user_id: int, db: Session = Depends(get_db)):
    follower_ids = [
        row[0]
        for row in db.query(Follower.follower_id)
        .filter(Follower.following_id == user_id)
        .all()
    ]
    users = db.query(User).filter(User.id.in_(follower_ids)).all()
    return [_enrich_user(db, u) for u in users]


@router.get("/{user_id}/following", response_model=list[UserResponse])
def get_following(user_id: int, db: Session = Depends(get_db)):
    following_ids = [
        row[0]
        for row in db.query(Follower.following_id)
        .filter(Follower.follower_id == user_id)
        .all()
    ]
    users = db.query(User).filter(User.id.in_(following_ids)).all()
    return [_enrich_user(db, u) for u in users]
