import asyncio
import aiohttp
import json
import argparse
import curses

ITEM_COLORS = {
    "crack": curses.COLOR_YELLOW,
    "trash": curses.COLOR_MAGENTA,
    "penguin": curses.COLOR_GREEN,
    "bike": curses.COLOR_BLUE,
    "water": curses.COLOR_CYAN,
    "barrier": curses.COLOR_MAGENTA,
    "car-0": curses.COLOR_WHITE,
    "car-1": curses.COLOR_RED,
    "car-2": curses.COLOR_WHITE,
    "car-3": curses.COLOR_RED,
}
COLOR_INDEX = {key: idx for idx, key in enumerate(ITEM_COLORS, 1)}


def update_screen(stdscr, data):
    """
    Update the terminal screen with game data.

    This function clears the terminal screen and then displays the game's dashboard
    and track matrix. The dashboard displays the remaining time and player details
    such as name, car number, and score. The track matrix displays the game's track
    with obstacles and player cars.

    Args:
        stdscr (curses.window): The window object representing the terminal screen.
        data (dict): The game data received from the server. This data contains
                     details about the game's state, including time left, player details,
                     and track matrix.
    """
    stdscr.clear()

    # Display dashboard
    payload = data.get("payload", {})
    timeleft = payload.get("timeleft")
    stdscr.addstr(f"Time Left: {timeleft}\n")

    players = payload.get("players", [])
    for player in players:
        player_name = player.get("name")
        player_car = player.get("car")
        player_score = player.get("score")
        stdscr.addstr(f"car-{player_car}: {player_name}, Score: {player_score}\n")

    stdscr.addstr("\n")

    # Display track as 8x3 matrix
    track = [["          " for _ in range(6)] for _ in range(9)]
    for item in payload.get("track", []):
        x, y = item["x"], item["y"]
        if 0 <= x < 6 and 0 <= y < 9:
            track[y][x] = item["name"].center(10)

    # Add players cars to the track
    for player in players:
        x, y = player["x"], player["y"]
        if 0 <= x < 6 and 0 <= y < 9:
            track[y][x] = f"car-{player['car']}".center(10)

    for row in track:
        stdscr.addstr(" | ")
        for cell in row[:3]:
            color_idx = COLOR_INDEX.get(cell.strip(), 0)
            stdscr.addstr(cell, curses.color_pair(color_idx) | curses.A_BOLD)
            stdscr.addstr(" | ")
        stdscr.addstr(" | ")
        for cell in row[3:]:
            color_idx = COLOR_INDEX.get(cell.strip(), 0)
            stdscr.addstr(cell, curses.color_pair(color_idx) | curses.A_BOLD)
            stdscr.addstr(" | ")

        stdscr.addstr("\n")

    stdscr.refresh()


async def websocket_client(url, stdscr, drivers, fps):
    """
    Connect to a game server, parse received JSON updates, and pretty print them.

    Args:
        url (str): The game server URL.
        stdscr: The curses screen object.
        drivers (list): List of driver URLs.
    """
    async with aiohttp.ClientSession() as session:
        # Initialize the game
        await initialize_game(session, url, drivers, fps)

        async with session.ws_connect(f"{url}/ws") as ws:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    try:
                        update_screen(stdscr, data)
                    except Exception as e:
                        print(f"Error: {e}")
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print("WebSocket error:", ws.exception())


async def initialize_game(session, url, drivers, fps):
    """
    Initialize the game by sending POST requests to the server.

    Args:
        session (aiohttp.ClientSession): The active aiohttp session.
        url (str): The game server URL.
        drivers (list): List of driver URLs.
    """
    drivers_driver_query = ",".join(drivers)
    await session.post(f"{url}/admin?drivers={drivers_driver_query}")
    await asyncio.sleep(2)  # Wait for 2 seconds
    await session.post(f"{url}/admin?running=1")
    await session.post(f"{url}/admin?rate={fps}")


def init_colors():
    """
    Initialize the color pairs for the curses environment.
    """
    curses.start_color()

    # Initialize colors for items
    for idx, color in enumerate(ITEM_COLORS.values(), 1):
        curses.init_pair(idx, color, curses.COLOR_BLACK)


def main(stdscr):
    """
    The main function for the ROSE game client.

    This function initializes the game client, parses command-line arguments,
    sets up the display, and starts the WebSocket client to connect to the game server.

    Args:
    - stdscr (curses.window): The main curses window object, used for drawing game elements.

    Command-line Arguments:
    --url: The game server URL to connect to. This argument is required.
    --drivers: URLs of one or two drivers. This argument is required.
    --fps: Frames per second for the game display. Choices are [1, 2, 5, 10]. Default is 5.

    Example Usage:
    python main.py --url ws://game-server-url --drivers http://driver1-url http://driver2-url --fps 5

    """
    parser = argparse.ArgumentParser(description="ROSE game client.")
    parser.add_argument("--url", required=True, help="Game server URL to connect to.")
    parser.add_argument(
        "--drivers", required=True, nargs="+", help="URLs of one or two drivers."
    )
    parser.add_argument(
        "--fps",
        type=int,
        choices=[1, 2, 5, 10],
        default=5,
        help="Frames per second for the game display. Choices are [1, 2, 5, 10].",
    )

    args = parser.parse_args()

    init_colors()  # Initialize the color pairs

    stdscr.clear()
    stdscr.addstr("Connecting...\n")
    stdscr.refresh()

    asyncio.get_event_loop().run_until_complete(
        websocket_client(args.url, stdscr, args.drivers, args.fps)
    )


if __name__ == "__main__":
    curses.wrapper(main)
