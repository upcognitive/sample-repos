"""CLI entry point for Orkest."""

import sys


def main() -> None:
    """Run the Orkest CLI."""
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        import uvicorn

        uvicorn.run("orkest.api.router:app", host="0.0.0.0", port=8000, reload=False)
        return

    print("Orkest CLI")
    print("Usage: orkest serve  # start the API server")


if __name__ == "__main__":
    main()
