import os

TORTOISE_ORM = {
    "connections": {"default": os.environ.get("DATABASE_URL")},
    # replace with settings
    "apps": {
        "models": {
            "models": ["app.models.tortoise", "aerich.models"],
            "default_connection": "default",
        }
    },
}
