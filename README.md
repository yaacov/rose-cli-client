# ROSE CLI Client

The command-line client for the ROSE game, demo the posibility of writing stand alone user interfaces, graphical, command line, and 3rd party web based UIs.

## Description

The rose-cli-client is a command-line interface for the ROSE game. It initializes the game client, parses command-line arguments, sets up the display, and starts the WebSocket client to connect to the game server.
Installation

![](https://github.com/yaacov/rose-cli-client/blob/b58a766518a893b6f221f20fc07747686ae4209d/demo.gif)

## Running Containerized:

First, start the ROSE server and some drivers running on localhost:

``` bash
# Start student A driver container
podman run --rm --network host -e PORT=8001 -it quay.io/rose/rose-game-ai-reference:latest

# Start student B driver container
podman run --rm --network host -it quay.io/yaacov/rose-go-driver:latest --port 8082

# Start server container
podman run --rm --network host -it quay.io/rose/rose-game-engine:latest
```

Then, start the command-line client:

``` bash
podman run --network host --rm -it quay.io/rose/rose-cli-client \
    --url http://127.0.0.1:8880 \
    --drivers http://127.0.0.1:8081 http://127.0.0.1:8082
```

## Clone the repository:

``` bash
git clone https://github.com/yaacov/rose-cli-client.git
```

## Navigate to the project directory:

``` bash
cd rose-cli-client
```

## Install the required packages:

``` bash
pip install -r requirements.txt
```
## Usage

To start the game client, use the following command:

``` bash
python main.py --url ws://game-server-url \
   --drivers http://driver1-url http://driver2-url --fps 5
```

### Command-line Arguments

- `--url`: The game server URL to connect to. This argument is required.
- `--drivers`: URLs of one or two drivers. This argument is required.
- `--fps`: Frames per second for the game display. Choices are [1, 2, 5, 10]. Default is 5.
