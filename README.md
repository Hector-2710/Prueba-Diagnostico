# Mining Visualizer

Real-time analysis of the most used words in function names from GitHub repositories.

## Quick Start

```bash
docker-compose up --build
```

Open http://localhost:8000

## How to Use

1. **Start the Miner**: Click the "Detenido" button
2. **Configure N**: Select how many words to display (default 10)
3. **Visualize**: The table updates in real-time

## Features

- Extracts function names from Python and Java repositories
- Real-time table with the most frequent words
- Start/stop control of the miner from the UI
- Configurable N words selector

## Structure

```
├── miner/           # Extracts functions from GitHub
├── visualizer/      # FastAPI dashboard + WebSocket
├── requirements.txt
└── docker-compose.yml
```
