"""
Auto Reddit Commenter
Posts one AI-generated comment to Reddit on random sub-reddit
"""

import asyncio
import random
import sys
from datetime import datetime

from app.async_reddit_client import AsyncRedditClient
from app.constants import (
    DEFAULT_COMMENT_LIMIT,
    DEFAULT_POST_LIMIT,
)
from app.llm_client import LLMClient
from app.logger import init_logger

# Daily commenter configuration
SUBREDDITS = ["AskReddit", "askmen", "YouShouldKnow", "programming", "todayilearned"]

TONES = ["auto", "funny", "analytical", "controversial"]

ENABLE_POSTING_HOURS = (9, 18)  # 9 AM to 6 PM

logger = init_logger(__name__)

# Global clients (similar to routes.py pattern)
reddit_client = None
llm_client = None


async def get_reddit_client():
    """Get or create Reddit client instance"""
    global reddit_client
    if reddit_client is None:
        reddit_client = AsyncRedditClient()
    return reddit_client


async def get_llm_client():
    """Get or create LLM client instance"""
    global llm_client
    if llm_client is None:
        llm_client = LLMClient()
    return llm_client


async def cleanup():
    """Clean up resources"""
    global reddit_client
    if reddit_client:
        await reddit_client.close()
        reddit_client = None


def select_random_subreddit() -> str:
    """Select a random subreddit from the predefined list"""
    selected = random.choice(SUBREDDITS)
    logger.info(f"Selected subreddit: r/{selected}")
    return selected


def select_random_tone() -> str:
    """Select a random comment tone"""
    selected = random.choice(TONES)
    logger.info(f"Selected tone: {selected}")
    return selected


def is_posting_time() -> bool:
    """Check if current time is within allowed posting hours"""
    current_hour = datetime.now().hour
    start_hour, end_hour = ENABLE_POSTING_HOURS
    is_allowed = start_hour <= current_hour < end_hour
    if not is_allowed:
        logger.info(
            f"Current time ({current_hour}:xx) is outside posting hours ({start_hour}:00-{end_hour}:00)"
        )
    return is_allowed


async def get_posts_from_subreddit(subreddit: str):
    """Fetch top posts from a subreddit"""
    try:
        reddit_client = await get_reddit_client()
        posts = await reddit_client.get_top_posts(subreddit, limit=DEFAULT_POST_LIMIT)
        if not posts:
            raise Exception("No posts found or subreddit not accessible")

        return posts
    except Exception as e:
        logger.error(f"Error fetching posts from r/{subreddit}: {e}")
        raise


async def get_post_details(post):
    """Fetch detailed post information with comments"""
    try:
        reddit_client = await get_reddit_client()

        # Load the post fully (similar to routes.py)
        full_post = await reddit_client.get_submission_by_id(post.id)

        post_data = await reddit_client.get_post_data(full_post)
        comments_data = await reddit_client.get_top_comments(
            full_post, limit=DEFAULT_COMMENT_LIMIT
        )

        post_data["comments"] = comments_data
        return post_data
    except Exception as e:
        logger.error(f"Error fetching post details: {e}")
        raise


async def select_random_post(subreddit: str):
    """Select a random suitable post from subreddit"""
    try:
        posts = await get_posts_from_subreddit(subreddit)
        llm_client = await get_llm_client()
        reddit_client = await get_reddit_client()

        # Filter suitable posts
        suitable_posts = []
        for post in posts:
            post_data = await reddit_client.get_post_data(post)

            relevance = llm_client.analyze_post_relevance(post_data)
            if relevance["suitable"]:
                suitable_posts.append(post)

        if not suitable_posts:
            logger.warning(f"No suitable posts found in r/{subreddit}")
            return None

        selected_post = random.choice(suitable_posts)
        return selected_post

    except Exception as e:
        logger.error(f"Error selecting post from r/{subreddit}: {e}")
        return None


async def generate_and_post_comment(dry_run: bool = True):
    """Main function to generate and post a daily comment"""
    try:
        # Check posting time (skip for dry runs)
        if not dry_run and not is_posting_time():
            logger.info("Skipping posting - outside of allowed hours")
            return False

        # Select random subreddit and post
        subreddit = select_random_subreddit()

        # Try up to 3 different subreddits if needed
        post = None
        for attempt in range(3):
            if attempt > 0:
                logger.info(f"Attempt {attempt + 1}: Trying different subreddit...")
                subreddit = select_random_subreddit()

            post = await select_random_post(subreddit)
            if post:
                break

        if not post:
            logger.error("Failed to select a suitable post from any subreddit")
            return False

        # Get clients and post data
        reddit_client = await get_reddit_client()
        llm_client = await get_llm_client()

        post = await reddit_client.get_submission_by_id(post.id)
        post_data = await reddit_client.get_post_data(post)
        logger.info(f"Selected post: {post_data['title']}")
        comments_data = await reddit_client.get_top_comments(
            post, limit=DEFAULT_COMMENT_LIMIT
        )

        # Select random tone and generate comment
        tone = select_random_tone()

        logger.info("Generating comment...")
        result = llm_client.generate_comment(post_data, comments_data, tone=tone)

        if not result["success"]:
            logger.error(f"Comment generation failed: {result['error']}")
            return False

        logger.info(f"Generated {result['tone']} comment ({result['length']} chars)")
        logger.info(f"Comment preview: {result['comment'][:100]}...")

        # Post comment
        logger.info(f"Posting comment (dry_run={dry_run})...")
        post_result = await reddit_client.post_comment(
            post_data["id"], result["comment"], dry_run=dry_run
        )

        if post_result["success"]:
            if dry_run:
                logger.info("✅ Dry run completed successfully!")
            else:
                logger.info("✅ Comment posted successfully!")
                if "comment_url" in post_result:
                    logger.info(f"Comment URL: {post_result['comment_url']}")

            # Log summary
            logger.info(f"""
Daily Comment Summary:
- Subreddit: r/{subreddit}
- Post: {post_data["title"][:60]}...
- Post Score: {post_data["score"]}
- Post Comments: {post_data["num_comments"]}
- Tone: {result["tone"]}
- Comment: {result["comment"]}
- Posted: {"No (dry run)" if dry_run else "Yes"}
            """)
            return True
        else:
            logger.error(f"Failed to post comment: {post_result['error']}")
            return False

    except Exception as e:
        logger.error(f"Daily commenting task failed: {e}")
        return False

    finally:
        await cleanup()


async def main():
    """Main entry point"""
    logger.info("=== Daily Reddit Commenter Started ===")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")

    # Parse command line arguments for dry_run mode
    dry_run = "--live" not in sys.argv  # Default to dry run for safety

    if dry_run:
        logger.info("🔄 Running in DRY RUN mode (no actual posting)")
    else:
        logger.info("🚀 Running in LIVE mode (will actually post)")

    success = await generate_and_post_comment(dry_run=dry_run)

    if success:
        logger.info("=== Daily Reddit Commenter Completed Successfully ===")
    else:
        logger.error("=== Daily Reddit Commenter Failed ===")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
