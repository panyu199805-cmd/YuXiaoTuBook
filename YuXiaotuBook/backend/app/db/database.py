from app.core.config import settings

TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}


async def init_db() -> None:
    from tortoise import Tortoise

    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)


async def close_db() -> None:
    from tortoise import Tortoise

    await Tortoise.close_connections()
