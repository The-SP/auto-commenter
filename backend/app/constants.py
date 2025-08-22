"""Application-wide constants and configuration values"""

# Reddit API Limits and Defaults
DEFAULT_POST_LIMIT = 3
DEFAULT_COMMENT_LIMIT = 5
MAX_COMMENT_LENGTH = 10000  # Reddit's actual limit

# Application Behavior
DEFAULT_DRY_RUN = True
MIN_POST_SCORE = 5
MIN_POST_COMMENTS = 3
MIN_TITLE_LENGTH = 10

# Comment Content Filters
DELETED_CONTENT = ["[deleted]", "[removed]", ""]
LINK_POST_PLACEHOLDER = "[Link/Image Post]"

# LLM Settings
DEFAULT_TEMPERATURE = 0.7
MAX_LLM_TOKENS = 1000
MIN_COMMENT_LENGTH = 10
