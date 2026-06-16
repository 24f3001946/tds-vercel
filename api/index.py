from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"]
)

with open("telemetry.json","r") as f:
    telemetry=json.load(f)

class RequestData(BaseModel):
    regions:list[str]
    threshold_ms:int

@app.post("/")
async def analytics(data:RequestData):

    result=[]

    for region in data.regions:

        rows=[x for x in telemetry if x["region"]==region]

        latency=[x["latency_ms"] for x in rows]
        uptime=[x["uptime"] for x in rows]

        result.append({
            "region":region,
            "avg_latency":round(sum(latency)/len(latency),2),
            "p95_latency":round(float(np.percentile(latency,95)),2),
            "avg_uptime":round(sum(uptime)/len(uptime),2),
            "breaches":sum(
                1 for x in latency
                if x>data.threshold_ms
            )
        })

    return result
