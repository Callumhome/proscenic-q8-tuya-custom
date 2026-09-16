import argparse

from fastapi import FastAPI, HTTPException

from services.robot_service import robot_service, RobotService


app = FastAPI()


# --------------------------------------------------
# API routes
# --------------------------------------------------

@app.get("/robot/clean/{room}")
def api_clean_room(room: str):
    response = robot_service.clean_room(room)

    if not response.get("success", False) and "error" in response:
        raise HTTPException(
            status_code=500,
            detail=response,
        )

    return response


@app.get("/robot/mop")
def api_mop():
    response = robot_service.mop()

    if not response.get("success", False):
        raise HTTPException(
            status_code=500,
            detail=response,
        )

    return response


@app.get("/robot/stop")
def api_return_to_base():
    response = robot_service.return_to_base()

    if not response.get("success", False):
        raise HTTPException(
            status_code=500,
            detail=response,
        )

    return response


# --------------------------------------------------
# CLI
# --------------------------------------------------

_ROOM_HINT = " | ".join(
    f"{k}={v}" for k, v in RobotService.ROOM_NAMES.items()
)

COMMANDS = {
    "clean": f"Clean a room by ID or name. Usage: clean <id/name> | {_ROOM_HINT}",
    "mop": "Start whole-map Mop mode.",
    "stop": "Return the robot to its base.",
    "help": "Show this help message.",
    "exit": "Exit the program.",
}


def _print_help():
    print("Available commands:")
    for name, description in COMMANDS.items():
        print(f" {name:<8} {description}")
    print()


def _handle(line: str) -> bool:
    parts = line.strip().split()

    if not parts:
        return True

    cmd = parts[0].lower()
    args = parts[1:]

    if cmd in ("exit", "quit"):
        return False

    if cmd == "help":
        _print_help()

    elif cmd == "clean":
        if not args:
            print(f"Usage: clean <id/name> | {_ROOM_HINT}")
        else:
            response = robot_service.clean_room(args[0])
            print(response)

    elif cmd == "mop":
        response = robot_service.mop()
        print(response)

    elif cmd == "stop":
        response = robot_service.return_to_base()
        print(response)

    else:
        print(
            f"Unknown command: '{cmd}'. "
            "Type 'help' for available commands."
        )

    return True


def run_cli():
    print("Proscenic Q8 - CLI controller")
    print("Type 'help' for commands, 'exit' to quit.")
    print()

    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not _handle(line):
            break


# --------------------------------------------------
# Entry point
# --------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Proscenic Q8 Tuya controller"
    )

    parser.add_argument(
        "--mode",
        choices=["cli", "api"],
        default="cli",
        help="Startup mode: 'cli' (default) or 'api'.",
    )

    args = parser.parse_args()

    if args.mode == "api":
        import uvicorn

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8111,
        )
    else:
        run_cli()
