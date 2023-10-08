import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

# always mix potions
# 500ml a barrel, 100ml a potion, and 30g a barrel
sql = """
SELECT num_red_ml, num_red_potions FROM global_inventory
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
    
    pots = potions_delivered[0].quantity
    ml = 100 * pots
    
    
    sql = """
        UPDATE global_inventory
        SET 
            num_red_ml = {},
            num_red_potions = {}
        WHERE id = 0;
        """.format(first_row.num_red_ml - ml, first_row.num_red_potions + pots)
    
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

    pots = 0
    if (first_row.num_red_ml >= 100):
        pots, ml = first_row.num_red_ml / 100, first_row.num_red_ml % 100

    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": pots
            }
        ]
