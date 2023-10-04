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
        potions = first_row.num_red_potions



router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.

    return [
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": potions,
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            }
        ]
