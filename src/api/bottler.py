import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

# always mix potions
# 500ml a barrel, 100ml a potion, and 30g a barrel
sql = """
SELECT num_red_ml, num_red_potions, num_green_ml, num_green_potions, num_blue_ml, num_blue_potions FROM global_inventory
"""

with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
        first_row = result.first()
        

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print(potions_delivered)
    
    for potion in potions_delivered:
        if potion.potion_type == [100,0,0,0]:
            quantity, ml = first_row.num_red_ml // 100, first_row.num_red_ml % 100
            potion_name = "red"
            pots = potions_delivered[0].quantity
        elif potion.potion_type == [0,100,0,0]:
            quantity, ml = first_row.num_green_ml // 100, first_row.num_green_ml % 100
            potion_name = "green"
            pots = potions_delivered[0].quantity
        elif potion.potion_type == [0,0,100,0]:
            quantity, ml = first_row.num_blue_ml // 100, first_row.num_blue_ml % 100
            potion_name = "blue"
            pots = potions_delivered[0].quantity
        
        sql = """
        UPDATE global_inventory
        SET 
            num_{}_ml = {},
            num_{}_potions = {}
        WHERE id = 0;
        """.format(potion_name, ml,
                   potion_name, quantity + pots)
        print(sql)
    
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text(sql))
    
    
    
        
    return "OK"

# Gets called 4 times a day
# 
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    poss_barrel = [first_row.num_red_ml,first_row.num_green_ml,first_row.num_blue_ml]
    pot_type = [[100,0,0,0],[0,100,0,0],[0,0,100,0]]
    out = []
    pots = 0
    c = 0
    for pot in poss_barrel:
        if (pot >= 100):
            pots = pot / 100
        out.append(
            {
                "potion_type": pot_type[c],
                "quantity": pots
            }
        )
        c+=1
            

    return out
