import os
from collections import Counter
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

word_counter = Counter()
connected_clients = []

@app.get("/")
async def get():
    return HTMLResponse(content=open(os.path.join(os.path.dirname(__file__), 'static', 'index.html')).read())

@app.post("/api/data")
async def receive_data(data: dict):
    """Recibe datos del miner y los distribuye a clientes WebSocket"""
    words = data.get('words', [])
    word_counter.update(words)
    
    for client in connected_clients[:]:
        try:
            await client.send_json({
                'type': 'update',
                'repo': data.get('repo', ''),
                'language': data.get('language', ''),
                'word_count': len(words),
                'data': get_top_words(50)
            })
        except Exception:
            try:
                connected_clients.remove(client)
            except ValueError:
                pass
    
    return {'status': 'received'}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        await websocket.send_json({
            'type': 'init',
            'data': get_top_words(50)
        })
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

@app.get("/api/words")
async def get_words(top: int = 50):
    return get_top_words(top)

def get_top_words(n=50):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    top = word_counter.most_common(n)
    return {
        'timestamp': now,
        'total_words': sum(word_counter.values()),
        'unique_words': len(word_counter),
        'top': [{'word': w, 'count': c} for w, c in top]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
