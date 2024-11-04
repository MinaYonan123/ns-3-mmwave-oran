# Copyright (c) 2024 Orange Innovation Poland
# Author: jerzy.jegier@orange.com
import os
from typing import List

from pathlib import Path as OsPath

import uvicorn, json, glob
from fastapi import FastAPI, HTTPException, Path, Body
from api import api
from pydantic import BaseModel

app = FastAPI()


class PolicyTypeSchema(BaseModel):
    name: str
    description: str
    policy_type_id: int
    create_schema: dict


class PolicyInstanceSchema(BaseModel):
    threshold: int


class StatusResponse(BaseModel):
    enforceStatus: str
    enforceReason: str


policy_types = {}
policy_instances = {}


@app.get("/a1-p/healthcheck")
async def get_healthcheck():
    return {"status": "A1 is healthy"}


@app.get("/a1-p/policytypes", response_model=List[int])
async def get_all_policy_types():
    return list(policy_types.keys())


@app.get("/a1-p/policytypes/{policy_type_id}", response_model=PolicyTypeSchema)
async def get_policy_type(policy_type_id: int = Path(..., gt=0, lt=2147483647)):
    if policy_type_id not in policy_types:
        raise HTTPException(status_code=404, detail="Policy type not found")
    return policy_types[policy_type_id]


@app.put("/a1-p/policytypes/{policy_type_id}", response_model=PolicyTypeSchema)
async def create_policy_type(policy_type_id: int = Path(..., gt=0, lt=2147483647),
                             body: PolicyTypeSchema = Body(...)):
    if policy_type_id in policy_types:
        raise HTTPException(status_code=400, detail="Policy type already existed")
    policy_types[policy_type_id] = body
    policy_instances[policy_type_id] = {}
    return body


@app.put("/a1-p/policytypes/{policy_type_id}/policies/{policy_instance_id}", response_model=PolicyInstanceSchema)
async def create_policy_instance(policy_type_id: int, policy_instance_id: str, body: PolicyInstanceSchema = Body(...)):
    if policy_type_id in policy_types:
        policy_instances[policy_type_id][policy_instance_id] = body
    else:
        raise HTTPException(status_code=400, detail="Policy type does not exist")
    return body


@app.get("/a1-p/policytypes/{policy_type_id}/policies/{policy_instance_id}/status", response_model=PolicyInstanceSchema)
async def get_policy_instance_status(policy_type_id: int, policy_instance_id: str):
    if policy_type_id in policy_types:
        if policy_instance_id in policy_instances[policy_type_id]:
            return policy_instances[policy_type_id][policy_instance_id]
        else:
            raise HTTPException(status_code=400, detail="Policy instance does not exist")
    else:
        raise HTTPException(status_code=400, detail="Policy type does not exist")


@app.get("/a1-p/policytypes/{policy_type_id}/policies", response_model=List[str])
async def list_policy_instances(policy_type_id: int):
    if policy_type_id not in policy_types:
        raise HTTPException(status_code=400, detail="Policy type does not exist")
    return list(policy_instances[policy_type_id].keys())


@app.delete("/a1-p/policytypes/{policy_type_id}")
async def delete_policy_type(policy_type_id: int = Path(..., gt=0, lt=2147483647)):
    if policy_type_id not in policy_types:
        raise HTTPException(status_code=404, detail="Policy type not found")
    if policy_type_id in policy_instances:
        raise HTTPException(status_code=400, detail="Policy type cannot be deleted because there are instances")
    del policy_types[policy_type_id]
    return {"detail": "Policy type successfully deleted"}


@app.delete("/a1-p/policytypes/{policy_type_id}/policies/{policy_instance_id}")
async def delete_policy_instance(policy_type_id: int, policy_instance_id: str):
    if policy_type_id not in policy_types:
        raise HTTPException(status_code=404, detail="Policy type not found")
    if policy_instance_id not in policy_instances[policy_type_id]:
        raise HTTPException(status_code=400, detail="Policy instance not found")
    del policy_instances[policy_type_id][policy_instance_id]
    return {"detail": "Policy instance successfully deleted"}


@app.get("/")
async def read_root():
    return {"message": "O-RAN Non-RT RIC API"}


@app.post("/a1-p/policytypes/create/{policy_type_id}")
async def create_policy(item: PolicyTypeSchema, policy_type_id: str):
    api.create_policy(item, policy_type_id)


@app.post("/a1-p/policytypes/update/{policy_type_id}/{threshold}")
async def update_policy(policy_type_id: str, threshold: str):
    api.update_policy(policy_type_id, threshold)


@app.delete("/a1-p/policytypes/delete/{policy_type_id}")
async def delete_policy(policy_type_id: str):
    api.delete_policy(policy_type_id)


path = "../policies/"


def load_policies():
    pattern = os.path.join(path, '*.json')
    for filename in glob.glob(pattern):
        with open(filename, "r") as outfile:
            json_object = json.load(outfile)
            policy_type_id = int(OsPath(filename).stem)
            policy_types[policy_type_id] = PolicyTypeSchema(**json_object)
            policy_instances[policy_type_id] = {}


def store_policy(item: PolicyTypeSchema, policy_type_id: str):
    with open(path + policy_type_id + ".json", "w") as outfile:
        json.dump(item.model_dump_json(), outfile)


if __name__ == "__main__":
    load_policies()
    uvicorn.run(app, host="0.0.0.0", port=9000)
