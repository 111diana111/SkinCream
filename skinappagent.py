from flask import Flask, jsonify, request
from uagents import Agent, Context, Model, Bureau
from uagents.setup import fund_agent_if_low


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


SkinAppAgent = Agent(
    name="SkinAppAgent",
    port=8006,
    seed="skin recovery phrase",
    endpoint="something")

# Registering and funding the agent on Almanac
fund_agent_if_low(SkinAppAgent.wallet.address())
print(SkinAppAgent.wallet.address())

@SkinAppAgent.on_event("startup")
async def agent_details(ctx: Context):
    ctx.logger.info(f' Skin Agent Address is {SkinAppAgent.address}')

# Initialise storage keys
@SkinAppAgent.on_event("startup")
async def initialize_storage(ctx: Context):
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

main_app_query_proto = Protocol()


@main_app_query_proto.on_message(model=DataRequest, replies={DataResponse})
async def handle_main_app_query_request(ctx: Context, sender: str, msg: DataRequest):
    ctx.logger.info(f'Fetching results for {msg.product_name}')
    routine_data = await set_parameters()
    await ctx.send(sender, DataResponse(routine_data))



SkinAppAgent.include(main_app_query_proto)

if __name__ == '__main__':
    SkinAppAgent.run()

