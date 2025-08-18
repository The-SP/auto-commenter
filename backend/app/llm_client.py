from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from .config import settings
from .logger import init_logger
from .prompts import AUTO_SELECT_USER, COMMENT_GENERATION_USER, TONE_PROMPTS

logger = init_logger(__name__)


class LLMClient:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")

        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7,
            max_tokens=1000,
        )
        logger.info(
            f"Initialized Gemini LLM client with model: {settings.GEMINI_MODEL}"
        )

    def get_available_tones(self):
        """Get list of available comment tones"""
        return list(TONE_PROMPTS.keys())

    def generate_comment(self, post_data, existing_comments=None, tone="auto"):
        """Generate a contextual comment for a Reddit post with specified tone"""

        # Validate tone
        if tone not in TONE_PROMPTS:
            logger.warning(f"Unknown tone '{tone}', defaulting to 'auto'")
            tone = "auto"

        # Format comments section
        comments_section = ""
        if existing_comments:
            comments_section = "\n\nTop existing comments:\n"
            for i, comment in enumerate(existing_comments, 1):
                comments_section += f"{i}. [{comment['score']}] {comment['body']}...\n"

        # Use appropriate prompt template
        if tone == "auto":
            user_prompt = AUTO_SELECT_USER.format(
                title=post_data["title"],
                content=post_data["content"][:500],
                subreddit=post_data["subreddit"],
                score=post_data["score"],
                num_comments=post_data["num_comments"],
                comments_section=comments_section,
            )
        else:
            user_prompt = COMMENT_GENERATION_USER.format(
                tone=tone,
                title=post_data["title"],
                content=post_data["content"][:500],
                subreddit=post_data["subreddit"],
                score=post_data["score"],
                num_comments=post_data["num_comments"],
                comments_section=comments_section,
            )

        try:
            messages = [
                SystemMessage(content=TONE_PROMPTS[tone]),
                HumanMessage(content=user_prompt),
            ]

            response = self.llm.invoke(messages)
            comment_text = response.content.strip()

            # Basic validation
            if len(comment_text) < 10:
                raise ValueError("Generated comment too short")

            logger.info(f"Generated {tone} comment: {comment_text}")
            return {
                "success": True,
                "comment": comment_text,
                "length": len(comment_text),
                "tone": tone,
            }

        except Exception as e:
            error_msg = f"Failed to generate {tone} comment: {e}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "tone": tone}

    def analyze_post_relevance(self, post_data):
        """Analyze if a post is suitable for commenting"""

        # Skip very low engagement posts
        if post_data["score"] < 5 and post_data["num_comments"] < 3:
            return {"suitable": False, "reason": "Low engagement (score/comments)"}

        # Skip deleted/removed content
        if post_data["content"] in ["[deleted]", "[removed]", ""]:
            return {"suitable": False, "reason": "No content available"}

        # Check title length (avoid very short titles)
        if len(post_data["title"]) < 10:
            return {"suitable": False, "reason": "Title too short"}

        return {"suitable": True, "reason": "Post appears suitable for commenting"}
