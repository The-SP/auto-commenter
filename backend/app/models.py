from typing import List, Optional

from pydantic import BaseModel


class PostSummary(BaseModel):
    id: str
    title: str
    score: int
    num_comments: int
    subreddit: str


class Comment(BaseModel):
    id: str
    body: str
    score: int
    author: str
    created_utc: float


class PostDetails(BaseModel):
    id: str
    title: str
    content: str
    url: str
    score: int
    num_comments: int
    subreddit: str
    comments: List[Comment]


class GenerateCommentRequest(BaseModel):
    post_id: str
    tone: str = "auto"


class GenerateCommentResponse(BaseModel):
    success: bool
    comment: Optional[str] = None
    length: Optional[int] = None
    tone: str
    error: Optional[str] = None


class PostCommentRequest(BaseModel):
    post_id: str
    comment_text: str
    dry_run: bool = True


class PostCommentResponse(BaseModel):
    success: bool
    comment_id: Optional[str] = None
    comment_url: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
