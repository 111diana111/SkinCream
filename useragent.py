from datetime import datetime, timedelta
from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low
from random import uniform
import asyncio

class SkinStatus(Model):
    hydration: int
    elasticity: float
    collagen_density: float
    day: str

class QuerySkinRequest(Model):
    day: str

class QuerySkinResponse(Model):
    parameters: list

class ErrorResponse(Model):
    error: str

# Define human skin parameters async function
async def set_parameters(day):
    daily_values = []
    current_day = datetime.fromisoformat(day)

    for _ in range(365):
        hydration = round(uniform(12, 37), 2)
        elasticity = round(uniform(0.04, 0.70), 2)
        collagen_density = round(uniform(2.10, 3.30), 2)

        daily_values.append(SkinStatus(day=current_day.isoformat(), hydration=hydration, elasticity=elasticity, collagen_density=collagen_density))
        current_day -= timedelta(days=1)

    return daily_values

# Test function
async def test_set_parameters():
    today = datetime.now().isoformat()
    result = await set_parameters(today)
    print(result)

# Define User Agent
UserAgent = Agent(
    name="UserAgent",
    port=8002,
    seed="skin_data_day1",
    endpoint="app account"
)

# Registering and funding the agent on Almanac
fund_agent_if_low(UserAgent.wallet.address())

# Initialise storage keys
@UserAgent.on_event("startup")
async def agent_details(ctx: Context):
    ctx.logger.info(f'User Agent Address is {UserAgent.address}')

@UserAgent.on_event("startup")
async def initialize_storage(ctx: Context):
    ctx.storage.set("day", "0")
    ctx.storage.set("hydration", 12)
    ctx.storage.set("elasticity", 0.04)
    ctx.storage.set("collagen", 2.10)

skin_query_proto = Protocol()

@skin_query_proto.on_query(model=QuerySkinRequest, replies=QuerySkinResponse)
async def handle_skin_query_request(ctx: Context, sender: str, msg: QuerySkinRequest):
    try:
        ctx.logger.info(f"Fetching results for {msg.day}.")
        parameters = await set_parameters(msg.day)
        ctx.logger.info(parameters)
        await ctx.send(sender, QuerySkinResponse(parameters=parameters))

    except Exception as e:
        error_message = f'Error fetching job details : {str(e)}'
        ctx.logger.error(error_message)
        await ctx.send(sender, ErrorResponse(response=error_message))

UserAgent.include(skin_query_proto)

if __name__ == '__main__':
    asyncio.run(test_set_parameters())
    UserAgent.run()
