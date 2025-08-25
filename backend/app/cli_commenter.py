"""
Interactive Reddit Commenter
Posts AI-generated comments to Reddit with human oversight
"""

import asyncio

from .async_reddit_client import AsyncRedditClient
from .constants import DEFAULT_COMMENT_LIMIT, DEFAULT_POST_LIMIT
from .llm_client import LLMClient
from .logger import init_logger

logger = init_logger(__name__)

# Global clients
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


def display_posts(posts_data):
    """Display post titles with indices"""
    print(f"\nTop {len(posts_data)} posts:")
    for i, post_data in enumerate(posts_data, 1):
        print(f"{i}. {post_data['title']}")
        print(f"   Score: {post_data['score']} | Comments: {post_data['num_comments']}")
        print()


def display_post_details(post_data):
    """Display full post details and comments"""
    print("=" * 80)
    print(f"TITLE: {post_data['title']}")
    print(f"SUBREDDIT: r/{post_data['subreddit']}")
    print(f"SCORE: {post_data['score']} | COMMENTS: {post_data['num_comments']}")
    print(f"URL: {post_data['url']}")
    print("-" * 80)
    print(f"CONTENT:\n{post_data['content']}")
    print("-" * 80)

    if post_data["comments"]:
        print(f"TOP COMMENTS ({len(post_data['comments'])}):")
        for i, comment in enumerate(post_data["comments"], 1):
            print(f"\n{i}. [{comment['score']}] by u/{comment['author']}:")
            print(f"{comment['body']}")
    else:
        print("No comments found.")
    print("=" * 80)


def display_tone_options(tones):
    """Display available comment tones"""
    print("\nAvailable comment tones:")
    tone_descriptions = {
        "auto": "Let AI choose the best tone",
        "supportive": "Encouraging and empathetic",
        "funny": "Humorous and witty",
        "analytical": "Thoughtful and detailed",
        "questioning": "Curious and probing",
        "informative": "Educational and helpful",
        "controversial": "Challenging and thought-provoking",
    }

    for i, tone in enumerate(tones, 1):
        description = tone_descriptions.get(tone, "")
        print(f"{i}. {tone.upper()}: {description}")
    print()


def get_user_choice(prompt, min_val, max_val):
    """Get valid user choice within range"""
    while True:
        try:
            choice = int(input(prompt))
            if min_val <= choice <= max_val:
                return choice
            print(f"Please enter a number between {min_val} and {max_val}")
        except ValueError:
            print("Please enter a valid number")


def get_yes_no(prompt):
    """Get yes/no response from user"""
    while True:
        response = input(prompt).lower().strip()
        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False
        print("Please enter 'y' or 'n'")


async def get_posts_from_subreddit(subreddit: str):
    """Fetch top posts from a subreddit"""
    try:
        reddit_client = await get_reddit_client()
        posts = await reddit_client.get_top_posts(subreddit, limit=DEFAULT_POST_LIMIT)
        if not posts:
            raise Exception("No posts found or subreddit not accessible")

        # Convert to post data
        posts_data = []
        for post in posts:
            post_data = await reddit_client.get_post_data(post)
            posts_data.append(post_data)

        logger.info(f"Fetched {len(posts_data)} posts from r/{subreddit}")
        return posts, posts_data
    except Exception as e:
        logger.error(f"Error fetching posts from r/{subreddit}: {e}")
        raise


async def get_post_with_comments(post, post_data):
    """Get detailed post with comments"""
    try:
        reddit_client = await get_reddit_client()

        print("\nFetching comments for selected post...")
        comments_data = await reddit_client.get_top_comments(
            post, limit=DEFAULT_COMMENT_LIMIT
        )

        post_data["comments"] = comments_data
        logger.info(f"Fetched {len(comments_data)} comments for post {post_data['id']}")
        return post_data
    except Exception as e:
        logger.error(f"Error fetching comments: {e}")
        raise


async def generate_comment_for_post(post_data, tone: str):
    """Generate comment with specified tone"""
    try:
        llm_client = await get_llm_client()

        # Check if post is suitable
        relevance = llm_client.analyze_post_relevance(post_data)
        if not relevance["suitable"]:
            print(f"\n⚠️  Warning: {relevance['reason']}")
            if not get_yes_no("Continue anyway? (y/n): "):
                return None

        print(f"\n🤖 Generating {tone} comment...")
        result = llm_client.generate_comment(
            post_data, post_data["comments"], tone=tone
        )

        if not result["success"]:
            print(f"❌ Comment generation failed: {result['error']}")
            return None

        return result
    except Exception as e:
        logger.error(f"Error generating comment: {e}")
        return None


async def post_comment_to_reddit(post_data, comment_text, dry_run: bool = True):
    """Post comment to Reddit"""
    try:
        reddit_client = await get_reddit_client()

        action = "🔥 DRY RUN -" if dry_run else "🚀"
        print(f"\n{action} Posting comment...")

        result = await reddit_client.post_comment(
            post_data["id"], comment_text, dry_run=dry_run
        )

        if result["success"]:
            if dry_run:
                print("✅ Dry run completed successfully!")
            else:
                print("✅ Comment posted successfully!")
                if "comment_url" in result:
                    print(f"URL: {result['comment_url']}")
        else:
            print(f"❌ Failed to post: {result['error']}")

        return result
    except Exception as e:
        logger.error(f"Error posting comment: {e}")
        return {"success": False, "error": str(e)}


async def main():
    """Main interactive commenter function"""
    try:
        logger.info("=== Interactive Reddit Commenter Started ===")
        print("🤖 Welcome to Reddit Auto Commenter!")

        # Get subreddit name
        subreddit = input("Enter subreddit name (without r/): ").strip()
        if not subreddit:
            print("Subreddit name cannot be empty")
            return

        # Get top posts
        print(f"\nFetching top posts from r/{subreddit}...")
        try:
            posts, posts_data = await get_posts_from_subreddit(subreddit)
        except Exception as e:
            print(f"Failed to fetch posts: {e}")
            return

        if not posts_data:
            print("No posts found or error occurred")
            return

        # Display posts and get selection
        display_posts(posts_data)
        choice = get_user_choice(
            f"Select post (1-{len(posts_data)}): ", 1, len(posts_data)
        )
        selected_post_index = choice - 1
        selected_post = posts[selected_post_index]
        selected_post_data = posts_data[selected_post_index]

        # Fetch comments for selected post
        try:
            post = await reddit_client.get_submission_by_id(selected_post.id)
            selected_post_data = await get_post_with_comments(post, selected_post_data)
        except Exception as e:
            print(f"Failed to fetch comments: {e}")
            return

        # Display full post details
        display_post_details(selected_post_data)

        # Get available tones and let user select
        llm_client = await get_llm_client()
        available_tones = llm_client.get_available_tones()
        display_tone_options(available_tones)

        tone_choice = get_user_choice(
            f"Select comment tone (1-{len(available_tones)}): ", 1, len(available_tones)
        )
        selected_tone = available_tones[tone_choice - 1]

        # Generate comment
        result = await generate_comment_for_post(selected_post_data, selected_tone)
        if not result:
            return

        print(f"\n📝 Generated {result['tone']} comment ({result['length']} chars):")
        print("-" * 40)
        print(result["comment"])
        print("-" * 40)

        # Ask whether to post
        should_post = get_yes_no("\nPost this comment? (y/n): ")
        dry_run = not should_post

        # Post comment (either dry run or live)
        await post_comment_to_reddit(selected_post_data, result["comment"], dry_run)

        # Log summary
        logger.info(f"""
Comment Session Summary:
- Subreddit: r/{subreddit}
- Post: {selected_post_data["title"][:60]}...
- Post Score: {selected_post_data["score"]}
- Post Comments: {selected_post_data["num_comments"]}
- Tone: {result["tone"]}
- Comment: {result["comment"]}
- Posted: {"No (dry run)" if dry_run else "Yes"}
        """)

        print("\n✨ Session completed!")

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Interactive commenter failed: {e}")
        print(f"❌ Error: {e}")
    finally:
        await cleanup()


if __name__ == "__main__":
    asyncio.run(main())
