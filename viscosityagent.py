from datetime import *
from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low
from random import uniform
import asyncio


class ProductViscosity(Model):
    viscosity: float
    day: str


class ViscosityRequest(Model):
    product_name: str


class ViscosityResponse(Model):
    viscosity: float


class ErrorResponse(Model):
    error: str


# Define API connection (mock API)

# Define values in which the results should be returned
async def set_parameters(day):
    daily_values = []

    current_day = datetime.fromisoformat(day)
    for _ in range(365):
        viscosity = uniform(0, 23)

        daily_values.append(ProductViscosity(day=current_day.isoformat(),viscosity=viscosity))

        current_day -= timedelta(days=1)

    return daily_values

# Test function
async def test_set_parameters():
    today = datetime.now().isoformat()
    result = await set_parameters(today)
    print(result)

# Define User Agent

ViscosityAppAgent = Agent(
    name="ViscosityAppAgent",
    port=8000,
    seed="viscosity recovery phrase",
    endpoint="mock API")

# Registering and funding the agent on Almanac
fund_agent_if_low(ViscosityAppAgent.wallet.address())

@ViscosityAppAgent.on_event("startup")
async def agent_details(ctx: Context):
    ctx.logger.info(f' Viscosity Agent Address is {ViscosityAppAgent.address}')

# Initialise storage keys
@ViscosityAppAgent.on_event("startup")
async def initialize_storage(ctx: Context):
    ctx.storage.set("day", "0")
    ctx.storage.set("viscosity", 0)


viscosity_query_proto = Protocol()

@viscosity_query_proto.on_message(model=ViscosityRequest, replies=ViscosityResponse)
async def handle_viscosity_query_request(ctx: Context, sender: str, msg: ViscosityRequest):
    ctx.logger.info(f'Fetching results for {msg.product_name}')
    viscosity_data = await set_parameters()
    await ctx.send(sender, ViscosityResponse(viscosity_data))

ViscosityAppAgent.include(viscosity_query_proto)


if __name__ == '__main__':
    asyncio.run(test_set_parameters())
    ViscosityAppAgent.run()
