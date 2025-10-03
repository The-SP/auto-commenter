import asyncpraw

from app.core.config import settings
from app.core.constants import (
    DEFAULT_COMMENT_LIMIT,
    DEFAULT_DRY_RUN,
    DEFAULT_POST_LIMIT,
    DELETED_CONTENT,
    LINK_POST_PLACEHOLDER,
    MAX_COMMENT_LENGTH,
)
from app.core.logger import init_logger

logger = init_logger(__name__)


class AsyncRedditClient:
    def __init__(self):
        if not settings.REDDIT_CLIENT_ID:
            raise ValueError("REDDIT_CLIENT_ID is required")
        if not settings.REDDIT_CLIENT_SECRET:
            raise ValueError("REDDIT_CLIENT_SECRET is required")

        if settings.REDDIT_USERNAME and settings.REDDIT_PASSWORD:
            self.reddit = asyncpraw.Reddit(
                client_id=settings.REDDIT_CLIENT_ID,
                client_secret=settings.REDDIT_CLIENT_SECRET,
                username=settings.REDDIT_USERNAME,
                password=settings.REDDIT_PASSWORD,
                user_agent=settings.USER_AGENT,
            )
            self.can_post = True
            logger.info(
                f"Initialized async reddit client with posting capabilities for: {settings.REDDIT_USERNAME}"
            )
        else:
            # Read-only mode
            self.reddit = asyncpraw.Reddit(
                client_id=settings.REDDIT_CLIENT_ID,
                client_secret=settings.REDDIT_CLIENT_SECRET,
                user_agent=settings.USER_AGENT,
            )
            self.can_post = False
            logger.info("Initialized async client in read-only mode")

    async def close(self):
        """Close the Reddit session"""
        await self.reddit.close()

    async def get_top_posts(self, subreddit_name, limit=DEFAULT_POST_LIMIT):
        """Get top posts from subreddit in last 24 hours"""
        try:
            subreddit = await self.reddit.subreddit(subreddit_name)
            posts = []
            async for post in subreddit.top(time_filter="day", limit=limit):
                posts.append(post)
            logger.info(f"Fetched {len(posts)} posts from r/{subreddit_name}")
            return posts
        except Exception as e:
            logger.error(f"Failed to fetch posts from r/{subreddit_name}: {e}")
            return []

    async def get_post_data(self, post):
        """Extract relevant data from a Reddit post"""
        return {
            "id": post.id,
            "title": post.title,
            "content": post.selftext if post.selftext else LINK_POST_PLACEHOLDER,
            "url": post.url,
            "score": post.score,
            "num_comments": post.num_comments,
            "subreddit": str(post.subreddit),
        }

    async def get_top_comments(self, post, limit=DEFAULT_COMMENT_LIMIT):
        """Get top x comments from a post"""
        try:
            await post.comments.replace_more(limit=0)  # Remove "load more comments"

            comment_data = []
            for comment in post.comments[:limit]:
                # Skip deleted/removed comments
                if hasattr(comment, "body") and comment.body not in DELETED_CONTENT:
                    comment_data.append(
                        {
                            "id": comment.id,
                            "body": comment.body,
                            "score": comment.score,
                            "author": str(comment.author)
                            if comment.author
                            else "[deleted]",
                            "created_utc": comment.created_utc,
                        }
                    )

            logger.info(f"Fetched {len(comment_data)} comments for post {post.id}")
            return comment_data

        except Exception as e:
            logger.error(f"Failed to fetch comments for post {post.id}: {e}")
            return []

    async def get_post_with_comments(self, post, comment_limit=DEFAULT_COMMENT_LIMIT):
        """Get post data along with its top comments"""
        post_data = await self.get_post_data(post)
        post_data["comments"] = await self.get_top_comments(post, comment_limit)
        return post_data

    async def analyze_subreddit(
        self,
        subreddit_name,
        post_limit=DEFAULT_POST_LIMIT,
        comment_limit=DEFAULT_COMMENT_LIMIT,
    ):
        """Get posts and their comments for analysis"""
        posts = await self.get_top_posts(subreddit_name, post_limit)
        analyzed_posts = []

        for post in posts:
            post_with_comments = await self.get_post_with_comments(post, comment_limit)
            analyzed_posts.append(post_with_comments)

        logger.info(f"Analyzed {len(analyzed_posts)} posts from r/{subreddit_name}")
        return analyzed_posts

    async def post_comment(self, post_id, comment_text, dry_run=DEFAULT_DRY_RUN):
        """
        Post a comment to a Reddit submission

        Args:
            post_id (str): The ID of the Reddit post
            comment_text (str): The text content of the comment
            dry_run (bool): If True, only simulate posting without actually submitting

        Returns:
            dict: Result with success status and details
        """
        if not self.can_post:
            return {
                "success": False,
                "error": "Client not configured for posting. Initialize with bot username/password.",
                "error_type": "no_auth",
            }

        if dry_run:
            logger.info(f"DRY RUN - Would post comment to {post_id}:")
            logger.info(f"Comment: {comment_text[:100]}app..")
            return {
                "success": True,
                "comment_id": "dry_run_comment",
                "message": "Dry run completed successfully",
            }

        try:
            # Get the submission
            submission = await self.reddit.submission(id=post_id)

            # Validate comment text
            if not comment_text or not comment_text.strip():
                raise ValueError("Comment text cannot be empty")

            if len(comment_text) > MAX_COMMENT_LENGTH:
                raise ValueError(
                    f"Comment text too long (max {MAX_COMMENT_LENGTH:,} characters)"
                )

            # Post the comment
            comment = await submission.reply(comment_text)

            logger.info(f"Successfully posted comment {comment.id} to post {post_id}")
            return {
                "success": True,
                "comment_id": comment.id,
                "comment_url": f"https://reddit.com{comment.permalink}",
                "message": "Comment posted successfully",
            }

        except Exception as e:
            error_msg = f"Failed to post comment: {e}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "error_type": "error"}

    async def get_submission_by_id(self, post_id):
        """Get a submission by its ID"""
        try:
            submission = await self.reddit.submission(id=post_id)
            await submission.load()  # Load the submission data
            return submission
        except Exception as e:
            logger.error(f"Failed to get submission {post_id}: {e}")
            raise
