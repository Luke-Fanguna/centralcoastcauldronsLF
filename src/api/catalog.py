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
                "sku": "MINI_RED_BARREL",
                "ml_per_barrel": 200,
                "potion_type": [1, 0, 0, 0],
                "price": 60,
                "quantity": 1
            },
            {
                "sku": "RED_POT",
                "name": "red potion",
                "quantity": 1,
                "price": 20,
                "potion_type": [100, 0, 0, 0],
            },
            {
                "sku": "SMALL_RED_BARREL",
                "name": "red barrel",
                "quantity": 10,
                "price": 100,
                "potion_type": [1, 0, 0, 0],
            },
            {
                "sku": "MEDIUM_RED_BARREL",
                "name": "red barrel",
                "quantity": 10,
                "price": 250,
                "potion_type": [1, 0, 0, 0],
            },
            {
                "sku": "MINI_GREEN_BARREL",
                "name": "mini green barrel",
                "quantity": 1,
                "price": 60,
                "potion_type": [0, 1, 0, 0],
            },
            {
                "sku": "GREEN_POT",
                "name": "green potion",
                "quantity": 1,
                "price": 1,
                "potion_type": [0, 100, 0, 0],
            },
            {
                "sku": "SMALL_GREEN_BARREL",
                "name": "small green barrel",
                "quantity": 10,
                "price": 100,
                "potion_type": [0, 1, 0, 0],
            },
            {
                "sku": "MEDIUM_GREEN_BARREL",
                "name": "medium green barrel",
                "quantity": 10,
                "price": 250,
                "potion_type": [0, 1, 0, 0],
            },
            {
                "sku": "MINI_BLUE_BARREL",
                "name": "mini blue barrel",
                "quantity": 1,
                "price": 60,
                "potion_type": [0, 0, 1, 0],
            },
            {
                "sku": "BLUE_POT",
                "name": "blue potion",
                "quantity": 1,
                "price": 1,
                "potion_type": [0, 0, 100, 0],
            },
            {
                "sku": "SMALL_BLUE_BARREL",
                "name": "small blue barrel",
                "quantity": 10,
                "price": 120,
                "potion_type": [0, 0, 1, 0],
            },
            {
                "sku": "MEDIUM_BLUE_BARREL",
                "name": "medium blue barrel",
                "quantity": 10,
                "price": 300,
                "potion_type": [0, 0, 1, 0],
            }
        ]
