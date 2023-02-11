from typing import Union
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, ORJSONResponse
from service import start_monitor, blktrace_info, iostat_info

app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/start", response_class=ORJSONResponse)
async def start(url: Union[str, None] = Query(default=None, min_length=3, max_length=100), \
                datasetName: Union[str, None] = Query(default=None, min_length=3, max_length=100)):
    start_monitor(url, datasetName)
    return {"data": "successfully started"}

@app.get("/monitor/iostat", response_class=ORJSONResponse)
async def monitor_iostat():
    return iostat_info()

@app.get("/monitor/blktrace", response_class=ORJSONResponse)
async def monitor():
    return blktrace_info()
