from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Cookie, Form, UploadFile, File, Request
from pydantic import BaseModel
import pymongo
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
import datetime as dt

# Import scripts
import beta_version2
import funcs.profit_data_script as pds

# Setup app
app = FastAPI()

client = pymongo.MongoClient()
# Cors allowed origins
origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",  # Temporarily all because testing --> later on remember to change only localhost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""@app.get('/', status_code=200)
def render_machines(request: Request, response: Response):
    try:
        render_machines.list_of_sorted_machines = beta_version2.sort_machines()
        response.status_code = status.HTTP_200_OK
    except:
        response.status_code = status.HTTP_404_NOT_FOUND
    return render_machines.list_of_sorted_machines"""

"""@app.get('/{machine_name}', status_code=200)
def fetch_machine(machine_name: str, request: Request, response: Response):
    for machine in render_machines.list_of_sorted_machines:
        try:
            if machine['name'] == machine_name:
                response.status_code = status.HTTP_200_OK
                return machine
        except:
            response.status_code = status.HTTP_404_NOT_FOUND"""


@app.get("/api/profit_data")
async def profit_data(response: Response, country, coin=None, algorithm=None, machine_name=None):
    try:
        profit_json = await pds.main(country, coin, algorithm, machine_name)
        response.status_code = status.HTTP_200_OK
        return profit_json
    except:
        response.status_code = status.HTTP_400_BAD_REQUEST


@app.get("/api/machine_names")
async def machine_names(response: Response):
    try:
        machine_names_json = await pds.get_machine_names()
        response.status_code = status.HTTP_200_OK
        return machine_names_json
    except:
        response.status_code = status.HTTP_400_BAD_REQUEST


@app.get("/api/countries")
async def countries(response: Response):
    try:
        countries_json = await pds.get_countries()
        response.status_code = status.HTTP_200_OK
        return countries_json
    except:
        response.status_code = status.HTTP_400_BAD_REQUEST


@app.get("/api/algorithms")
async def algorithms(response: Response):
    try:
        algorithms_json = await pds.get_algorithms()
        response.status_code = status.HTTP_200_OK
        return algorithms_json
    except:
        response.status_code = status.HTTP_400_BAD_REQUEST


@app.get("/api/coins")
async def coins(response: Response):
    try:
        coins_json = await pds.get_coins()
        response.status_code = status.HTTP_200_OK
        return coins_json
    except:
        response.status_code = status.HTTP_400_BAD_REQUEST
