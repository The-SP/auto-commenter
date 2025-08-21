from typing import List

from fastapi import APIRouter, HTTPException

from .async_reddit_client import AsyncRedditClient
from .llm_client import LLMClient
from .logger import init_logger
from .models import (
    Comment,
    GenerateCommentRequest,
    GenerateCommentResponse,
    PostCommentRequest,
    PostCommentResponse,
    PostDetails,
    PostSummary,
)

logger = init_logger(__name__)
router = APIRouter()

# Global clients
reddit_client = None
llm_client = None


async def get_reddit_client():
    global reddit_client
    if reddit_client is None:
        reddit_client = AsyncRedditClient()
    return reddit_client


async def get_llm_client():
    global llm_client
    if llm_client is None:
        llm_client = LLMClient()
    return llm_client


@router.get("/")
async def root():
    return {"message": "Reddit Auto Commenter API"}


@router.get("/posts/{subreddit}", response_model=List[PostSummary])
async def get_posts(subreddit: str, limit: int = 3):
    """Fetch top posts from a subreddit"""
    try:
        reddit_client = await get_reddit_client()
        posts = await reddit_client.get_top_posts(subreddit, limit=limit)
        if not posts:
            raise HTTPException(
                status_code=404, detail="No posts found or subreddit not accessible"
            )

        post_summaries = []
        for post in posts:
            post_data = await reddit_client.get_post_data(post)
            post_summaries.append(
                PostSummary(
                    id=post_data["id"],
                    title=post_data["title"],
                    score=post_data["score"],
                    num_comments=post_data["num_comments"],
                    subreddit=post_data["subreddit"],
                )
            )

        return post_summaries

    except Exception as e:
        logger.error(f"Error fetching posts from r/{subreddit}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/post/{post_id}", response_model=PostDetails)
async def get_post_details(post_id: str):
    """Fetch detailed post information with comments"""
    try:
        reddit_client = await get_reddit_client()
        post = await reddit_client.get_submission_by_id(post_id)
        post_data = await reddit_client.get_post_data(post)
        comments_data = await reddit_client.get_top_comments(post, limit=5)

        # Convert to response model
        comments = [
            Comment(
                id=comment["id"],
                body=comment["body"],
                score=comment["score"],
                author=comment["author"],
                created_utc=comment["created_utc"],
            )
            for comment in comments_data
        ]

        return PostDetails(
            id=post_data["id"],
            title=post_data["title"],
            content=post_data["content"],
            url=post_data["url"],
            score=post_data["score"],
            num_comments=post_data["num_comments"],
            subreddit=post_data["subreddit"],
            comments=comments,
        )

    except Exception as e:
        logger.error(f"Error fetching post details for {post_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tones", response_model=List[str])
async def get_available_tones():
    """Get available comment tones"""
    try:
        reddit_client = await get_llm_client()
        tones = reddit_client.get_available_tones()
        return tones
    except Exception as e:
        logger.error(f"Error fetching tones: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-comment", response_model=GenerateCommentResponse)
async def generate_comment(request: GenerateCommentRequest):
    """Generate a comment for a post with specified tone"""
    try:
        reddit_client = await get_reddit_client()
        llm_client = await get_llm_client()

        # Get post data
        post = await reddit_client.get_submission_by_id(request.post_id)
        post_data = await reddit_client.get_post_data(post)
        comments_data = await reddit_client.get_top_comments(post, limit=5)

        # Check if post is suitable
        relevance = llm_client.analyze_post_relevance(post_data)
        if not relevance["suitable"]:
            return GenerateCommentResponse(
                success=False,
                tone=request.tone,
                error=f"Post not suitable: {relevance['reason']}",
            )

        # Generate comment
        result = llm_client.generate_comment(
            post_data, comments_data, tone=request.tone
        )

        return GenerateCommentResponse(
            success=result["success"],
            comment=result.get("comment"),
            length=result.get("length"),
            tone=result["tone"],
            error=result.get("error"),
        )

    except Exception as e:
        logger.error(f"Error generating comment: {e}")
        return GenerateCommentResponse(success=False, tone=request.tone, error=str(e))


@router.post("/post-comment", response_model=PostCommentResponse)
async def post_comment(request: PostCommentRequest):
    """Post a comment to Reddit"""
    try:
        reddit_client = await get_reddit_client()
        result = await reddit_client.post_comment(
            request.post_id, request.comment_text, dry_run=request.dry_run
        )

        return PostCommentResponse(
            success=result["success"],
            comment_id=result.get("comment_id"),
            comment_url=result.get("comment_url"),
            message=result.get("message"),
            error=result.get("error"),
            error_type=result.get("error_type"),
        )

    except Exception as e:
        logger.error(f"Error posting comment: {e}")
        return PostCommentResponse(
            success=False, error=str(e), error_type="server_error"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        reddit_client = await get_reddit_client()
        return {
            "status": "healthy",
            "can_post": getattr(reddit_client, "can_post", False),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "can_post": False,
        }
