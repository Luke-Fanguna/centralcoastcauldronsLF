import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

#goal: can only sell a barrel if total number of potions is less than 10

sql = """
    SELECT gold, num_red_ml, num_red_potions, num_green_ml, num_green_potions, num_blue_ml, num_blue_potions FROM global_inventory
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
    update_ml = {
        "red" : first_row.num_red_ml,
        "green" : first_row.num_green_ml,
        "blue" : first_row.num_blue_ml
    }

    for barrel in barrels_delivered:
        gold,ml = 0,0
        if barrel.potion_type == [1,0,0,0]:
            ml_type = "red"
        elif barrel.potion_type == [0,1,0,0]:
            ml_type = "green"
        elif barrel.potion_type == [0,0,1,0]:
            ml_type = "blue"
        gold += barrel.price
        ml += barrel.ml_per_barrel * barrel.quantity
        sql = """
            UPDATE global_inventory
            SET 
                gold = {},
                num_{}_ml = {}
            WHERE id = 0;
            """.format(first_row.gold - gold,ml_type,update_ml[ml_type] + ml)
        print(sql)
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text(sql))
    
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    
    purchased = []
    for barrel in wholesale_catalog:
        if barrel.potion_type == [1,0,0,0]:
            if first_row.num_red_potions < 10 and barrel.price < first_row.gold:
                purchased.append(
                    {
                        "sku": barrel.sku,
                        "quantity": barrel.quantity
                    }
                )
        elif barrel.potion_type == [0,1,0,0]:
            if first_row.num_green_potions < 10 and barrel.price < first_row.gold:
                purchased.append(
                    {
                        "sku": barrel.sku,
                        "quantity": barrel.quantity        
                    }
                )
        elif barrel.potion_type == [0,0,1,0]:
            if first_row.num_blue_potions < 10 and barrel.price < first_row.gold:
                purchased.append(
                    {
                        "sku": barrel.sku,
                        "quantity": barrel.quantity        
                    }
                )
    
    print(first_row.gold)
    return purchased
            

