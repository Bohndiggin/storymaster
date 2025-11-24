#!/usr/bin/env python3
"""
Standalone script to start the Storymaster sync server.
Useful for testing or running the sync server independently.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import uvicorn

from storymaster.sync_server.config import config


def main():
    """Start the sync server"""
    print("=" * 60)
    print("🚀 Starting Storymaster Sync Server")
    print("=" * 60)
    print(f"📡 Host: {config.HOST}")
    print(f"🔌 Port: {config.PORT}")
    print(f"🗄️  Database: {config.get_database_path()}")
    print("=" * 60)
    print()
    print("📱 To pair a mobile device:")
    print(f"   1. Open browser: http://localhost:{config.PORT}/api/pair/qr-image")
    print("   2. Scan QR code with mobile app")
    print("   3. Device will be paired automatically")
    print()
    print("📖 API Documentation: http://localhost:{}/docs".format(config.PORT))
    print("🔍 Interactive API: http://localhost:{}/redoc".format(config.PORT))
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()

    try:
        uvicorn.run(
            "storymaster.sync_server.main:app",
            host=config.HOST,
            port=config.PORT,
            reload=config.RELOAD,
            log_level="info",
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down sync server...")
        sys.exit(0)


if __name__ == "__main__":
    main()
