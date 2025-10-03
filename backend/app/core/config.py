from decouple import config  # type: ignore


class Settings:
    # Reddit API
    REDDIT_CLIENT_ID = config("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = config("REDDIT_CLIENT_SECRET")
    USER_AGENT = config("USER_AGENT", default="AutoCommenter/1.0")

    # Reddit Authentication (for posting)
    REDDIT_USERNAME = config("REDDIT_USERNAME")
    REDDIT_PASSWORD = config("REDDIT_PASSWORD")

    # Future: Gemini API
    GEMINI_API_KEY = config("GEMINI_API_KEY")
    GEMINI_MODEL = config("GEMINI_MODEL", default="gemini-2.0-flash")


settings = Settings()
