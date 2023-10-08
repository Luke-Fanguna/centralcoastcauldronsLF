import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

#goal: can only sell a barrel if total number of potions is less than 10

sql = """
    SELECT gold, num_red_ml, num_red_potions FROM global_inventory
    """

with db.engine.begin() as connection:
    result = connection.execute(sqlalchemy.text(sql))
    first_row = result.first()


router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int
    

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print(barrels_delivered)

    gold = 0
    ml = 0

    for barrel in barrels_delivered:
        gold += barrel.price
        ml += barrel.ml_per_barrel

    sql = """
        UPDATE global_inventory
        SET 
            gold = {},
            num_red_ml = {}
        WHERE id = 0;
    """.format(first_row.gold - gold,
               first_row.num_red_ml + ml)
    
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(sql))
    
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    choice = None
    pots = first_row.num_red_potions
    gold = first_row.gold
    purchased = []
    
    if pots < 10:
        for barrel in wholesale_catalog:
            if choice is None:
                if barrel.price < gold:
                    choice = barrel
            else:
                if barrel.price < choice.price and barrel.ml_per_barrel > choice.ml_per_barrel:
                    choice = barrel      
        if choice is not None:
            purchased = [
                        {
                        "sku": choice.sku,
                        "quantity": 1
                        }
                        ]
    
    return purchased
            

