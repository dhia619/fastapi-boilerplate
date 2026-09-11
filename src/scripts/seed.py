import asyncio
import logging

from src.config import get_settings
from src.database import db_session, engine
from src.core.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


async def main():
    try:
        async with db_session() as db:
            await db.commit()
            logger.info("Seeding completed successfully.")
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())