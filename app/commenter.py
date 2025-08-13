from llm_client import LLMClient
from logger import init_logger
from reddit_client import RedditClient

logger = init_logger(__name__)


def display_posts(posts):
    """Display post titles with indices"""
    print(f"\nTop {len(posts)} posts:")
    for i, post_data in enumerate(posts, 1):
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


def main():
    # Initialize clients
    try:
        reddit_client = RedditClient()
        llm_client = LLMClient()
    except Exception as e:
        logger.error(f"Failed to initialize clients: {e}")
        return

    # Get subreddit name
    subreddit = input("Enter subreddit name (without r/): ").strip()
    if not subreddit:
        print("Subreddit name cannot be empty")
        return

    # Get top posts (without comments initially)
    print(f"\nFetching top posts from r/{subreddit}...")
    posts = reddit_client.get_top_posts(subreddit, limit=3)

    if not posts:
        print("No posts found or error occurred")
        return

    # Convert to basic post data
    posts_data = [reddit_client.get_post_data(post) for post in posts]

    # Display posts and get selection
    display_posts(posts_data)
    choice = get_user_choice(f"Select post (1-{len(posts_data)}): ", 1, len(posts_data))
    selected_post_index = choice - 1
    selected_post = posts_data[selected_post_index]

    # Now fetch comments for the selected post
    print("\nFetching comments for selected post...")
    selected_post["comments"] = reddit_client.get_top_comments(
        posts[selected_post_index], limit=5
    )

    # Display full post details
    display_post_details(selected_post)

    # Check if post is suitable
    relevance = llm_client.analyze_post_relevance(selected_post)
    if not relevance["suitable"]:
        print(f"\n⚠️  Warning: {relevance['reason']}")
        if not get_yes_no("Continue anyway? (y/n): "):
            return

    # Get available tones and let user select
    available_tones = llm_client.get_available_tones()
    display_tone_options(available_tones)

    tone_choice = get_user_choice(
        f"Select comment tone (1-{len(available_tones)}): ", 1, len(available_tones)
    )
    selected_tone = available_tones[tone_choice - 1]

    # Generate comment with selected tone
    print(f"\n🤖 Generating {selected_tone} comment...")
    result = llm_client.generate_comment(
        selected_post, selected_post["comments"], tone=selected_tone
    )

    if not result["success"]:
        print(f"❌ Comment generation failed: {result['error']}")
        return

    print(f"\n📝 Generated {result['tone']} comment ({result['length']} chars):")
    print("-" * 40)
    print(result["comment"])
    print("-" * 40)

    # Ask whether to post
    should_post = get_yes_no("\nPost this comment? (y/n): ")

    if should_post:
        print("🚀 Posting comment...")
        post_result = reddit_client.post_comment(
            selected_post["id"], result["comment"], dry_run=False
        )

        if post_result["success"]:
            print("✅ Comment posted successfully!")
            if "comment_url" in post_result:
                print(f"URL: {post_result['comment_url']}")
        else:
            print(f"❌ Failed to post: {post_result['error']}")
    else:
        post_result = reddit_client.post_comment(
            selected_post["id"], result["comment"], dry_run=True
        )


if __name__ == "__main__":
    main()
