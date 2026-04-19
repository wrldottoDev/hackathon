from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.post import Post
from ..models.report import Report
from ..models.user import User
from ..schemas.post import PostCreate, PostResponse

router = APIRouter(prefix="/posts", tags=["feed"])


def _enrich_post(db: Session, post: Post) -> PostResponse:
    author = db.query(User).filter(User.id == post.author_id).first()
    reports_count = db.query(Report).filter(Report.post_id == post.id).count()
    return PostResponse(
        id=post.id,
        author_id=post.author_id,
        author_username=author.username if author else "",
        author_display_name=author.display_name if author else "",
        author_profile_picture=author.profile_picture_url if author else "",
        image_url=post.image_url,
        caption=post.caption,
        likes_count=post.likes_count,
        reports_count=reports_count,
        created_at=post.created_at,
    )


@router.post("", response_model=PostResponse, status_code=201)
def create_post(
    author_id: int = Query(...),
    payload: PostCreate = ...,
    db: Session = Depends(get_db),
):
    author = db.query(User).filter(User.id == author_id).first()
    if not author:
        raise HTTPException(404, "Author not found")
    post = Post(author_id=author_id, **payload.model_dump())
    db.add(post)
    db.commit()
    db.refresh(post)
    return _enrich_post(db, post)


@router.get("", response_model=list[PostResponse])
def list_posts(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(limit).all()
    return [_enrich_post(db, p) for p in posts]


@router.get("/feed/{user_id}", response_model=list[PostResponse])
def get_user_feed(
    user_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    posts = (
        db.query(Post)
        .order_by(Post.created_at.desc())
        .limit(limit)
        .all()
    )
    return [_enrich_post(db, p) for p in posts]


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(404, "Post not found")
    return _enrich_post(db, post)


@router.post("/{post_id}/like")
def like_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(404, "Post not found")
    post.likes_count += 1
    db.commit()
    return {"likes_count": post.likes_count}
