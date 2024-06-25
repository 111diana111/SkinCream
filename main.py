from flask import Flask, jsonify, request
from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low
from datetime import *
from random import uniform
from chemspipy import ChemSpider
import json


cs = ChemSpider('8L0LTGCA64VhQnlwKB9OPJcpVGN6XKqy')


#Define User Request and response

class SkinStatus(Model):
    hydration: int
    elasticity: float
    collagen_density: float
    day: str

class QuerySkinRequest(Model):
    day: str
    brand: str
    product: str

class QuerySkinResponse(Model):
    day: str
    brand: str
    product: str
    hydration: float
    elasticity: float
    collagen_density: float
    absorption_speed: float
    absorption_level: float

class ErrorResponse(Model):
    error: str

#Define SkinApp Request and Response
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


class AppDataRequest(Model):
    day: str


class AppDataResponse(Model):
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

class AppErrorResponse(Model):
    error: str

class ProductFormula(Model):
    day: str
    brand: str
    product: str
    ingredients: list
    formula: list


class FormulaRequest(Model):
    brand: str
    product: str
    day: str

class FormulaResponse(Model):
    ingredients: list

class ErrorResponse(Model):
    error: str

#The Agents:

SkinAppAgent = Agent(name="SkinAppAgent", seed="skin recovery phrase")

UserAgent = Agent(name="UserAgent", seed="skin_data_day1")

ProductAgent = Agent(name="ProductAgent", seed="productdata_day1")

# Define addresses:

skin_address = "agent1q2u49qvajqzpds9yhm5f3y8wz86dhumxmqlusa6rxmxg557uj5sw55p844t"
user_address ="agent1q0wzslgquuhfykzsyj053jrtuf5vu7caftm7ghjv0vc7v8n0q8x25nuswcq"
product_address ="agent1qwmdwqt5adeduup748zvc0mfzxat3r4a3ssh5yk0fuzertza6df5yr4x2qy"

#Registration on Almanac
fund_agent_if_low(SkinAppAgent.wallet.address())
fund_agent_if_low(ProductAgent.wallet.address())
fund_agent_if_low(UserAgent.wallet.address())

#Initiation of the three agents

@UserAgent.on_event("startup")
async def user_details(ctx: Context):
    ctx.storage.set("day", "0")
    ctx.storage.set("hydration", 12)
    ctx.storage.set("elasticity", 0.04)
    ctx.storage.set("collagen", 2.10)
    ctx.logger.info(f'User Agent Address is {UserAgent.address}')

@SkinAppAgent.on_event("startup")
async def skinapp_details(ctx: Context):
    ctx.storage.set("day", "0")
    ctx.storage.set("hydration", 0)
    ctx.storage.set("elasticity", 0)
    ctx.storage.set("collagen_density", 0)
    ctx.storage.set("absorption_speed", 0)
    ctx.storage.set("absorption_level", 0)
    ctx.storage.set("product_brand", "0")
    ctx.storage.set("product_name", "0")
    ctx.storage.set("ingredients_name", "0")
    ctx.storage.set("ingredients_formula", "0")
    ctx.storage.set("density", 0)
    ctx.storage.set("viscosity", 0)
    ctx.storage.set("storage_area", "0")
    ctx.storage.set("temperature", "0")
    ctx.storage.set("humidity", "0")
    ctx.logger.info(f' Skin Agent Address is {SkinAppAgent.address}')

@ProductAgent.on_event("startup")
async def product_details(ctx: Context):
    ctx.storage.set("day", "0")
    ctx.storage.set("brand", "0")
    ctx.storage.set("product", "0")
    ctx.storage.set("ingredients", [])
    ctx.storage.set("formula", [])
    ctx.logger.info(f' Product Agent Address is {ProductAgent.address}')

# Establishing agent-specific protocols

user_query_proto = Protocol()
user_product_add = Protocol()
main_app_query_proto = Protocol()

# The UserAgent adds a new poduct to the SkinApp Agent's database:

@user_product_add.on_query(model=AppDataRequest)
def introduce_product(ctx:Context, sender:str, msg:AppDataRequest):
    with open("agent1q2u49qvajq_data.json.json") as file:
        query_records = json.load(file)
        current_day = datetime.fromisoformat(day)
        brand = input("Insert new product brand")
        product = input("Insert new product name")
        query_records["day"].append(current_day)
        query_records["brand"].append(brand)
        query_records["product"].append(product)

#The SkinApp agent sending a request to the Product Agent

@main_app_query_proto.on_message(model=FormulaRequest)
async def handle_product_queru_request(ctx:Context, sender:str, msg:AppDataRequest):
    brand_query = input("Please provide the product's brand")
    with open("agent1q2u49qvajq_data.json.json") as file:
        query_records = json.load(file)
        if query_records["brand"] == brand_query:
            ctx.logger.info(f'Fetching user skin status for {msg.brand}')
            await ctx.send(product_address, FormulaRequest(brand=brand_query))


@main_app_query_proto.on_message(model=FormulaResponse)
async def handle_product_query_response(ctx:Context, sender:str, msg:AppDataRequest):
    with open("csvjson.json") as file:
        skincare_data = json.load(file)
        for item in skincare_data:
            if item["brand"] == brand:
                ingredients = item['ingredients']
                ctx.logger.info(f'Fetching ingredients for {msg.brand} ')
                ctx.storage.set("ingredients", msg.ingredients)




UserAgent.include(user_query_proto)
UserAgent.include(user_product_add)
SkinAppAgent.include(main_app_query_proto)
SkinAppAgent.include(user_product_add)
ProductAgent.include(user_product_add)


if __name__ == '__main__':
    SkinAppAgent.run()

