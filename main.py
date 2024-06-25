from uagents import Agent, Context, Model, Protocol, Bureau
from uagents.setup import fund_agent_if_low
from datetime import *
from datetime import timedelta
from random import uniform
from chemspipy import ChemSpider
import json



# Setting the Default Data the app will compile from all agents
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


# Set up Data additions
class DataInsert(Model):
    day: str
    brand: str
    product: str

class NewDataConfirm(Model):
    success: bool

class DataRequest(Model):
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


class DataRetrieve(Model):
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


# The Agents:

SkinAppAgent = Agent(name="SkinAppAgent", seed="skin recovery phrase")

UserAgent = Agent(name="UserAgent", seed="skin_data_day1")

ProductAgent = Agent(name="ProductAgent", seed="productdata_day1")

# Define addresses:
skin_address = "agent1q2u49qvajqzpds9yhm5f3y8wz86dhumxmqlusa6rxmxg557uj5sw55p844t"
user_address = "agent1q0wzslgquuhfykzsyj053jrtuf5vu7caftm7ghjv0vc7v8n0q8x25nuswcq"
product_address = "agent1qwmdwqt5adeduup748zvc0mfzxat3r4a3ssh5yk0fuzertza6df5yr4x2qy"


# Initiation of the three agents
@UserAgent.on_event("startup")
async def user_startup(ctx: Context):
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
async def product_start_up(ctx: Context):
    ctx.logger.info(f' Product Agent Address is {ProductAgent.address}')

current_date = datetime.today().isoformat()
print(current_date)
product_brand = input("Insert new product brand")
print(product_brand)
product_name = input("Insert new product name")
print(product_name)

@UserAgent.on_message(model=DataInsert)
async def new_product_add(ctx: Context, sender: str, msg: DataInsert):
    await ctx.send(skin_address, DataInsert(day=current_date,brand=product_brand,product=product_name))
    ctx.logger.info(f"{msg.product} from  {msg.brand} stored on {msg.day}")

@SkinAppAgent.on_message(model=DataInsert)
async def new_product_response(ctx: Context, _sender: str, msg: DataInsert):
    ctx.storage.set("day", str(msg.day))
    ctx.storage.set("brand", str(msg.brand))
    ctx.storage.set("product", str(msg.product))
    ctx.logger.info(f"{msg.product} from {msg.brand} stored on {msg.day}")


bureau = Bureau(port=8009, endpoint="http://localhost:8007/submit")
bureau.add(SkinAppAgent)
bureau.add(UserAgent)
bureau.add(ProductAgent)

if __name__ == '__main__':
    bureau.run()
