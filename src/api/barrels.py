import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

#goal: can only sell a barrel if total number of potions is less than 10




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
    gold,red_ml,green_ml,blue_ml,evil_ml = 0,0,0,0,0
    for barrel in barrels_delivered:
        print(barrel)
        gold += barrel.price * barrel.quantity
        if barrel.potion_type == [1,0,0,0]:
            red_ml += barrel.ml_per_barrel * barrel.quantity
        elif barrel.potion_type == [0,1,0,0]:
            green_ml += barrel.ml_per_barrel * barrel.quantity
        elif barrel.potion_type == [0,0,1,0]:
            blue_ml += barrel.ml_per_barrel * barrel.quantity
        elif barrel.potion_type == [0,0,0,1]:
            evil_ml += barrel.ml_per_barrel * barrel.quantity

        with db.engine.begin() as connection:
            connection.execute(
                sqlalchemy.text("""
                UPDATE global_inventory
                SET 
                gold = gold - :gold,
                num_red_ml = num_red_ml + :red_ml,
                num_green_ml = num_green_ml + :green_ml,
                num_blue_ml = num_blue_ml + :blue_ml,
                num_evil_ml = num_evil_ml + :evil_ml
                """),[{"gold": gold, "red_ml":red_ml,"green_ml":green_ml,"blue_ml":blue_ml,"evil_ml":evil_ml}])
    
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
        SELECT gold, num_red_ml, num_green_ml, num_blue_ml, num_evil_ml FROM global_inventory
        """))
        inventory = result.first()
        
        potions_table = connection.execute(sqlalchemy.text("""
        SELECT sku, inventory
        FROM potions_table;
        """))
        
    pots = {}
    for i in potions_table:
        pots[i[0]] = i[1]

    print(wholesale_catalog)
    wallet = inventory.gold
    gold = 0
    purchased = []
    for barrel in wholesale_catalog:
        if barrel.potion_type == [1,0,0,0]:
            if  pots['R_POT'] < 10 and barrel.price < wallet:
                purchased.append(
                    {
                        "sku": barrel.sku,
                        "quantity": barrel.quantity
                    }
                )
                gold += barrel.price
                wallet -= barrel.price
        elif barrel.potion_type == [0,1,0,0]:
            if pots['G_POT'] < 10 and barrel.price < wallet:
                purchased.append(
                    {
                        "sku": barrel.sku,
                        "quantity": barrel.quantity        
                    }
                )
                gold += barrel.price
                wallet -= barrel.price
        elif barrel.potion_type == [0,0,1,0]:
            if pots['B_POT'] < 10 and barrel.price < wallet:
                purchased.append(
                    {
                        "sku": barrel.sku,
                        "quantity": barrel.quantity        
                    }
                )
                gold += barrel.price
                wallet -= barrel.price
        elif barrel.potion_type == [0,0,0,1]:
            if pots['EVIL_POT'] < 10 and barrel.price < wallet:
                purchased.append(
                    {
                        "sku": barrel.sku,
                        "quantity": barrel.quantity        
                    }
                )
                gold += barrel.price
                wallet -= barrel.price
    
    print(inventory.gold)
    return purchased
            

