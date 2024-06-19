import json
from flask import Flask, jsonify, request
from uagents import Agent, Context, Model, Bureau, Protocol
from uagents.setup import fund_agent_if_low
from uagents.query import query
import requests
import os
import jsonify
from flask_cors import CORS

app=Flask(__name__)
CORS(app)

# Define addresses:

skin_address = "agent1q2u49qvajqzpds9yhm5f3y8wz86dhumxmqlusa6rxmxg557uj5sw55p844t"
user_address ="agent1q0wzslgquuhfykzsyj053jrtuf5vu7caftm7ghjv0vc7v8n0q8x25nuswcq"
product_address ="agent1qwmdwqt5adeduup748zvc0mfzxat3r4a3ssh5yk0fuzertza6df5yr4x2qy"
environment_address ="agent1qvd29utqf756g8tlc3d7gxnvaxw8v86wnhx0u9ccd5kdesd39jh6z577phz"
viscosity_address ="agent1qvn9fzuzadjx3djsucwlkpn4w8wcpdutjtkt5ljjlksntvqqwk3ky9anm2y"
density_address = "agent1qtr5u00y2vhdprja5efvl6afa92zqtapr9u4lwg4vgq4njq8zx9wvmx0f3q"
#DoctorAgent.address ="agent1qtu3xyt9m0a4pdzpw4ehj0a8mjj3agfp0vmh0a6skh3w04w02vpkqnn9vjv"

# Define Request Response, and Error messages for the Skin App Agent:
class DefaultData(Model):
    day: str
    hydration: float
    elasticity: float
    collagen_density: float
    absorption_speed: float
    absorption_level: float
    brand: str
    product: str
    ingredients: list
    formula: list
    density: float
    viscosity: float
    storage_area: str
    temperature: float
    humidity: float


class DataRequest(Model):
    day: str


class DataResponse(Model):
    day: str
    hydration: float
    elasticity: float
    collagen_density: float
    absorption_speed: float
    absorption_level: float
    brand: str
    product: str
    ingredients: list
    formula: list
    density: float
    viscosity: float
    storage_area: str
    temperature: float
    humidity: float

class ErrorResponse(Model):
    error: str

# Define Request, Response and Error Models for the Product Agent
class FormulaRequest(Model):
    product_name: str

class FormulaResponse(Model):
    ingredients: list

class ErrorResponse(Model):
    error: str


# Define Request, Response and Error Models for the Density App
class DensityRequest(Model):
    product_name: str


class DensityResponse(Model):
    density: float


class ErrorResponse(Model):
    error: str

# # Define Request, Response and Error Models for the Viscosity App

class ViscosityRequest(Model):
    product_name: str


class ViscosityResponse(Model):
    viscosity: float


class ErrorResponse(Model):
    error: str


# Define Request, Response and Error Models for the User Agent

class QuerySkinRequest(Model):
    day: str


class QuerySkinResponse(Model):
    hydration: int
    elasticity: float
    collagen_density: float

class ErrorResponse(Model):
    error: str


# Define Request, Response and Error Models for the Smarthome data Agent
class EnvironmentRequest(Model):
    storage_place: str


class EnvironmentResponse(Model):
    temperature: int
    humidity: int
    day: str


class ErrorResponse(Model):
    error: str


SkinAppAgent = Agent(name="SkinAppAgent", seed="skin recovery phrase")

UserAgent = Agent(name="UserAgent", seed="skin_data_day1")

ProductAgent = Agent(name="ProductAgent", seed="productdata_day1")

EnvironmentAgent = Agent(name="EnvironmentAgent", seed="environmentaldata_day1")

DensityAppAgent = Agent(name="DensityAppAgent", seed="density recovery phrase")

ViscosityAppAgent = Agent(name="ViscosityAppAgent", seed="viscosity recovery phrase")



#Registration on Almanac
fund_agent_if_low(SkinAppAgent.wallet.address())
fund_agent_if_low(ProductAgent.wallet.address())
fund_agent_if_low(UserAgent.wallet.address())
fund_agent_if_low(DensityAppAgent.wallet.address())
fund_agent_if_low(ViscosityAppAgent.wallet.address())
fund_agent_if_low(EnvironmentAgent.wallet.address())



# The ProductAgent, the Viscosity App Agent, the Density App Agent, and the EnvironmentalAgent
# send their data to the Skin App every 28 days (the recommended interval for
# verifying the skin effectiveness of creams)

app_data_request = Protocol(name="app_data_request")


@app_data_request.on_message(model=DataRequest, replies=DataResponse)
async def handle_request(ctx: Context, sender: str, msg: DataRequest):
    await ctx.send(
        sender, DataResponse(text=f"Please return the requested data {ctx.agent.name}")
    )

ProductAgent.include(app_data_request)
DensityAppAgent.include(app_data_request)
ViscosityAppAgent.include(app_data_request)
EnvironmentAgent.include(app_data_request)





@SkinAppAgent.on_interval(period=1.0)
async def send_data(ctx: Context):
    status_list = await ctx.broadcast(app_data_request.digest, message=DataRequest)
    ctx.logger.info(f"Send to {len(status_list)} agents.")

@SkinAppAgent.on_message(model=DataResponse)
async def handle_response(ctx: Context, sender: str, msg: DataResponse):
    ctx.logger.info(f"Received response from {sender}: {msg.day}")

# Request by the User Agent towards the Skin App to retrive all collected data

bureau = Bureau(port=8007)
bureau.add(SkinAppAgent)
bureau.add(UserAgent)
bureau.add(ProductAgent)
bureau.add(EnvironmentAgent)
bureau.add(DensityAppAgent)
bureau.add(ViscosityAppAgent)

if __name__ == '__main__':
    bureau.run()

