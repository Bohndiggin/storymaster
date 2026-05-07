"""
Run the Storymaster sync server standalone.

Usage:
    python -m storymaster.sync_server

Honors STORYMASTER_DB_URL / STORYMASTER_DB_PATH for the backing database,
and STORYMASTER_SYNC_HOST / STORYMASTER_SYNC_PORT to override bind address.
"""

import os

import uvicorn

from storymaster.sync_server.config import config


def main() -> None:
    host = os.getenv("STORYMASTER_SYNC_HOST", config.HOST)
    port = int(os.getenv("STORYMASTER_SYNC_PORT", str(config.PORT)))

    uvicorn.run(
        "storymaster.sync_server.main:app",
        host=host,
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
