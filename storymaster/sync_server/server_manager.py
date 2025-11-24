"""Server manager for controlling the sync server lifecycle"""

import threading
import time
from typing import Optional

import uvicorn


class SyncServerManager:
    """Manages the FastAPI sync server lifecycle in a background thread"""

    def __init__(self):
        self.server: Optional[uvicorn.Server] = None
        self.server_thread: Optional[threading.Thread] = None
        self.is_running = False

    def start(self, host: str = "0.0.0.0", port: int = 8765) -> bool:
        """
        Start the sync server in a background thread.
        Returns True if server started successfully, False otherwise.
        """
        if self.is_running:
            print("⚠️  Sync server is already running")
            return False

        try:
            # Create uvicorn config
            config = uvicorn.Config(
                "storymaster.sync_server.main:app",
                host=host,
                port=port,
                log_level="info",
                access_log=False,  # Reduce noise in logs
            )

            # Create server instance
            self.server = uvicorn.Server(config)

            # Start server in background thread
            self.server_thread = threading.Thread(
                target=self._run_server, daemon=True, name="SyncServerThread"
            )
            self.server_thread.start()

            # Wait a bit to ensure server starts
            time.sleep(1)

            self.is_running = True
            print(f"🚀 Sync server started at http://{host}:{port}")
            return True

        except Exception as e:
            print(f"❌ Failed to start sync server: {e}")
            return False

    def _run_server(self):
        """Internal method to run the server (called in background thread)"""
        if self.server:
            self.server.run()

    def stop(self):
        """Stop the sync server gracefully"""
        if not self.is_running or not self.server:
            return

        try:
            print("🛑 Stopping sync server...")
            self.server.should_exit = True

            # Wait for server thread to finish (with timeout)
            if self.server_thread:
                self.server_thread.join(timeout=5)

            self.is_running = False
            print("✅ Sync server stopped")

        except Exception as e:
            print(f"⚠️  Error stopping sync server: {e}")

    def get_status(self) -> dict:
        """Get current server status"""
        return {
            "running": self.is_running,
            "thread_alive": self.server_thread.is_alive() if self.server_thread else False,
        }


# Global server manager instance
_server_manager: Optional[SyncServerManager] = None


def get_server_manager() -> SyncServerManager:
    """Get or create the global server manager instance"""
    global _server_manager
    if _server_manager is None:
        _server_manager = SyncServerManager()
    return _server_manager


def start_sync_server(host: str = "0.0.0.0", port: int = 8765) -> bool:
    """Convenience function to start the sync server"""
    manager = get_server_manager()
    return manager.start(host, port)


def stop_sync_server():
    """Convenience function to stop the sync server"""
    manager = get_server_manager()
    manager.stop()
