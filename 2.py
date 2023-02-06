from typing import Union
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, HTMLResponse, ORJSONResponse
from service import start_monitor, blktrace_info, iostat_info

app = FastAPI()

@app.post("/start", response_class=HTMLResponse)
async def start(url: Union[str, None] = Query(default=None, min_length=3, max_length=100), \
                datasetName: Union[str, None] = Query(default=None, min_length=3, max_length=100)):
    start_monitor(url, datasetName)
    return HTMLResponse(content="successfully started", status_code=200)

@app.get("/monitor/iostat", response_class=ORJSONResponse)
async def monitor_iostat():
    return iostat_info()

@app.get("/monitor/blktrace", response_class=ORJSONResponse)
async def monitor():
    return blktrace_info()
