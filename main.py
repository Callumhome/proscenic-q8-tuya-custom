import argparse
import sys
from fastapi import FastAPI, HTTPException
from services.robot_service import robot_service, RobotService

app = FastAPI()


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@app.get("/robot/clean/{room}")
def api_clean_room(room: str):
    response = robot_service.clean_room(room)
    if not response.get("success", False) and "error" in response:
        if response.get("code"):  # Tuya error code present
            raise HTTPException(status_code=500, detail=response)
    return response


@app.get("/robot/stop")
def api_return_to_base():
    response = robot_service.return_to_base()
    if not response.get("success", False) and "error" in response:
        if response.get("code"):  # Tuya error code present
            raise HTTPException(status_code=500, detail=response)
    return response


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

COMMANDS = {
    "clean": f"Clean a room. Usage: clean <room>  |  rooms: {', '.join(RobotService.ROOM_PAYLOAD)}",
    "stop":  "Return the robot to its base.",
    "help":  "Show this help message.",
    "exit":  "Exit the program.",
}


def _print_help():
    print("\nAvailable commands:")
    for name, description in COMMANDS.items():
        print(f"  {name:<8} {description}")
    print()


def _handle(line: str) -> bool:
    """Parse and execute one CLI line. Returns False when the user wants to exit."""
    parts = line.strip().split()
    if not parts:
        return True
    cmd, *args = parts

    if cmd in ("exit", "quit"):
        return False

    if cmd == "help":
        _print_help()

    elif cmd == "clean":
        if not args:
            print(f"Usage: clean <room>  |  rooms: {', '.join(RobotService.ROOM_PAYLOAD)}")
        else:
            response = robot_service.clean_room(args[0])
            print(response)

    elif cmd == "stop":
        response = robot_service.return_to_base()
        print(response)

    else:
        print(f"Unknown command: '{cmd}'. Type 'help' for available commands.")

    return True


def run_cli():
    print("Proscenic Q8 — CLI controller  (type 'help' for commands, 'exit' to quit)")
    _print_help()
    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not _handle(line):
            break


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Proscenic Q8 Tuya controller")
    parser.add_argument(
        "--mode",
        choices=["cli", "api"],
        default="cli",
        help="Startup mode: 'cli' (default) for interactive shell, 'api' to expose HTTP endpoints",
    )
    args = parser.parse_args()

    if args.mode == "api":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8111)
    else:
        run_cli()
