from flask import Flask
from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low
import json
import random
import requests
from chemspipy import ChemSpider


# The Product agent represents a compilation of data retrieved by the user
# from the viscosity and density apps
# Behaviours to attach:
# ingredients storage

cs = ChemSpider('8L0LTGCA64VhQnlwKB9OPJcpVGN6XKqy')


# Define Request, Response and Error Models

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

# Define function to fetch ingredients according to the user's input of brand and product

#Found this database on Kaggle. I'm not the author.

with open("csvjson.json") as file:
    skincare_data = json.load(file)

API_KEY = '8L0LTGCA64VhQnlwKB9OPJcpVGN6XKqy'
cs = ChemSpider(API_KEY)


def fetch_ingredients(brand, product):
    selected_product = {'brand': [], 'product': [], 'ingredients': []}

    for item in skincare_data:
        if brand in item['brand'] and product in item['name']:
            ing = item['ingredients']
            selected_product['brand'].append(brand)
            selected_product['product'].append(product)
            selected_product['ingredients'].append(ing)
            print(selected_product)

            for ingredient in ing.split(", "):
                try:
                    if isinstance(ingredient, str):
                        results = cs.search(ingredient)
                        if results:
                            for result in results:
                                formula = result.molecular_formula
                                print(f"Molecular formula for {ingredient}: {formula}")
                        else:
                            print(f"No results found for {ingredient}")
                    else:
                        print(f"Invalid ingredient format: {ingredient}")
                except Exception as e:
                    print(f"Error fetching data for {ingredient}: {str(e)}")


random_entry = random.choice(skincare_data)
random_brand = random_entry['brand']
random_product = random_entry['name']

fetch_ingredients(random_brand, random_product)



#Define Product Agent

ProductAgent = Agent(
    name="ProductAgent",
    port= 8004,
    seed="productdata_day1"
)

# Registering and funding the agent on Almanac
fund_agent_if_low(ProductAgent.wallet.address())

@ProductAgent.on_event("startup")
async def agent_details(ctx: Context):
    ctx.logger.info(f' Product Agent Address is {ProductAgent.address}')

# Initialise storage keys
@ProductAgent.on_event("startup")
async def initialize_storage(ctx: Context):
    ctx.storage.set("day", "0")
    ctx.storage.set("brand", "0")
    ctx.storage.set("product", "0")
    ctx.storage.set("ingredients", [])
    ctx.storage.set("formula", [])


formula_query_proto = Protocol()


@formula_query_proto.on_query(model=FormulaRequest, replies={FormulaResponse})
async def handle_formula_query_request(ctx: Context, sender:str, msg: FormulaRequest):
    try:
        ctx.logger.info(f"Fetching results for {msg.product} of {msg.brand} on {msg.day}.")
        parameters = await fetch_ingredients(msg.brand,msg.product)
        assert isinstance(parameters, object)
        ctx.logger.info(parameters)
        await ctx.send(sender, FormulaResponse(parameters=str(parameters)))

    except Exception as e:
        error_message = f'Error fetching job details : {str(e)}'
        ctx.logger.error(error_message)
        await ctx.send(sender, ErrorResponse(response = str(error_message)))

ProductAgent.include(formula_query_proto)

if __name__ == '__main__':
    ProductAgent.run()


