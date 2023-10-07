import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

# always mix potions
# 500ml and 30g
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
    print("potions",potions_delivered)

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
    if (first_row.num_red_ml == 100):
        pots, ml = first_row.num_red_ml / 500, first_row.num_red_ml % 500
        print(pots,ml)
    # connection.execute(sqlalchemy.text("UPDATE global_inventory\nSET num_red_ml = " + ml + "\nWHERE id = 0"))

    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": pots
            }
        ]
