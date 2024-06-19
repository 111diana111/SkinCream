# Import required libraries

from datetime import datetime, timedelta
from random import uniform
from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low
import asyncio


# Behaviours to attach:
# respond to requests for ambient data
# send ambient data


# Define Request, Response and Error Models
# Conventionally, the storage place (or the area of the house in which the user might keep their skincare) could be the
# bedroom, bathroom or fridge
class EnvironmentVariables(Model):
    temperature: float
    humidity: float
    day: str


class EnvironmentRequest(Model):
    storage_place: str


class EnvironmentResponse(Model):
    temperature: int
    humidity: int
    day: str


class ErrorResponse(Model):
    error: str


# Smart home data simulation for three different environments: fridge, bedroom, and bathroom

# values within the range had been calculated to also include the fridge, otherwise the
# values would have been 40-60 for humidity and 18 t0 23 for the interiors


async def set_parameters(day):
    daily_values = []

    current_day = datetime.fromisoformat(day)
    for _ in range(365):
        temperature = round(uniform(0, 23), 2)
        humidity = round(uniform(30, 60), 2)

        daily_values.append(EnvironmentVariables(day=current_day.isoformat(), temperature=temperature, humidity=humidity))
        current_day -= timedelta(days=1)

    return daily_values

# Test function
async def test_set_parameters():
    today = datetime.now().isoformat()
    result = await set_parameters(today)
    print(result)

# Define Environment Agent

EnvironmentAgent = Agent(
    name="EnvironmentAgent",
    port=8003,
    seed="environmentaldata_day1",
    endpoint="Smarthouse iCloud API"
)

# Registering and funding the agent on Almanac
fund_agent_if_low(EnvironmentAgent.wallet.address())


@EnvironmentAgent.on_event("startup")
async def agent_details(ctx: Context):
    ctx.logger.info(f'Environment Agent Address is {EnvironmentAgent.address}')


@EnvironmentAgent.on_event("startup")
async def initialize_storage(ctx: Context):
    ctx.storage.set("day", "0")
    ctx.storage.set("temperature", 0)
    ctx.storage.set("humidity", 30)


environment_query_proto = Protocol()


# On_query handler to the environment data on a provided date
@environment_query_proto.on_query(model=EnvironmentRequest, replies=EnvironmentResponse)
async def query_handler(ctx: Context, sender: str, msg: EnvironmentRequest):
    try:
        ctx.logger.info(f"Fetching results for {msg.storage_place}.")
        parameters = await set_parameters()
        ctx.logger.info(parameters)
        await ctx.send(sender, EnvironmentResponse(parameters=parameters))

    except Exception as e:
        error_message = f'Error fetching environmental data: {str(e)}'
        ctx.logger.error(error_message)
        await ctx.send(sender, ErrorResponse(error=error_message))


EnvironmentAgent.include(environment_query_proto)


if __name__ == '__main__':
    asyncio.run(test_set_parameters())
    EnvironmentAgent.run()
