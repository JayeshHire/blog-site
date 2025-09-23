from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

app.mount("/static", StaticFiles(directory="dist"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("./index.html", 'r') as f:
        content = f.read()
    return content

@app.post("/editorjs")
async def create_data(item = Body()):
    # data = json.loads(item))
    print(json.dumps(item, indent=3))
    return item