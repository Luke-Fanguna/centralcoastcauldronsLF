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
        connection.execute(sqlalchemy.text(
        """
        INSERT INTO gold_ledgers
        (gold)
        VALUES
        (:gold);
        INSERT INTO ml_ledgers
        (red_ml,green_ml,blue_ml,evil_ml)
        VALUES
        (:red_ml,:green_ml,:blue_ml,:evil_ml)
        """
        ),[{"gold":-gold,"red_ml":red_ml,"green_ml":green_ml,"blue_ml":blue_ml,"evil_ml":evil_ml}])
    
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    
    with db.engine.begin() as connection:
        barrels = connection.execute(sqlalchemy.text(
        """
        SELECT 
            SUM(red_ml) AS red,
            SUM(green_ml) AS green,
            SUM(blue_ml) AS blue,
            SUM(evil_ml) AS evil
        FROM ml_ledgers
        """
        )).fetchone()
        barrels = list(barrels)
        
        cash = connection.execute(sqlalchemy.text(
        """
        SELECT
            SUM(gold)
        FROM gold_ledgers
        """            
        )).fetchone()[0]
        

    wallet = cash
    gold = 0
    purchased = []
    for barrel in wholesale_catalog:
        if barrel.potion_type == [1,0,0,0]:
            if  barrels[0] < 100 and (barrel.price * barrel.quantity) < wallet:
                purchased.append(
                    {
                        "sku": barrel.sku,
                        "quantity": barrel.quantity
                    }
                )
                gold += barrel.price
                wallet -= barrel.price
        elif barrel.potion_type == [0,1,0,0]:
            if barrels[1] < 100 and (barrel.price * barrel.quantity) < wallet:
                purchased.append(
                    {
                        "sku": barrel.sku,
                        "quantity": barrel.quantity        
                    }
                )
                gold += barrel.price
                wallet -= barrel.price
        elif barrel.potion_type == [0,0,1,0]:
            if barrels[2] < 100 and (barrel.price * barrel.quantity) < wallet:
                purchased.append(
                    {
                        "sku": barrel.sku,
                        "quantity": barrel.quantity        
                    }
                )
                gold += barrel.price
                wallet -= barrel.price
        elif barrel.potion_type == [0,0,0,1]:
            if barrels[3] < 100 and (barrel.price * barrel.quantity) < wallet:
                purchased.append(
                    {
                        "sku": barrel.sku,
                        "quantity": barrel.quantity        
                    }
                )
                gold += barrel.price
                wallet -= barrel.price
    print("gold after purchasing: ",wallet)
    print("cost of barrels: ", gold)
    print("how much money i have: ", cash)
    print("barrels to be purchased: ", purchased)
    
    return purchased
            

