import sqlalchemy
from src import database as db
from fastapi import APIRouter

# goal: how many potions do we currently have

sql = """
SELECT num_red_potions FROM global_inventory
"""

with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(sql))
            first_row = result.first()
            
router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.

    return [
            {
                "sku": "RED_POT",
                "name": "red potion",
                "quantity": 1,
                "price": 20,
                "potion_type": [100, 0, 0, 0],
            },
            {
                "sku": "BIG_RED",
                "name": "red barrel",
                "quantity": 1,
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            },
            {
                "sku": "GREEN_POT",
                "name": "green potion",
                "quantity": 1,
                "price": 30,
                "potion_type": [0, 100, 0, 0],
            },
            {
                "sku": "BIG_GREEN",
                "name": "green barrel",
                "quantity": 1,
                "price": 70,
                "potion_type": [0, 100, 0, 0],
            },
            {
                "sku": "BLUE_POT",
                "name": "blue potion",
                "quantity": 1,
                "price": 30,
                "potion_type": [0, 0, 100, 0],
            },
            {
                "sku": "BIG_BLUE",
                "name": "blue barrel",
                "quantity": 1,
                "price": 70,
                "potion_type": [0, 0, 100, 0],
            }
        ]
