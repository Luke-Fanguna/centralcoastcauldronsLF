import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import ast

# always mix potions
# 500ml a barrel, 100ml a potion, and 30g a barrel

        

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

    with db.engine.begin() as connection:
        print(potions_delivered)
        
        # additional_potions = sum(potion.quantity for potion in potions_delivered)
        num_red_ml = sum(potion.quantity * potion.potion_type[0] for potion in potions_delivered)
        num_green_ml = sum(potion.quantity * potion.potion_type[1] for potion in potions_delivered)
        num_blue_ml = sum(potion.quantity * potion.potion_type[2] for potion in potions_delivered)
        num_evil_ml = sum(potion.quantity * potion.potion_type[3] for potion in potions_delivered)


        
        for potion_delivered in potions_delivered:
            connection.execute(
                sqlalchemy.text("""
                                UPDATE potions_table
                                SET inventory = inventory + :additional_potions
                                WHERE type = :potion_type
                                """),
                [{"additional_potions":potion_delivered.quantity,
                  "potion_type":str(potion_delivered.potion_type)}])
            
        connection.execute(
            sqlalchemy.text("""
                            UPDATE global_inventory
                            SET
                                num_red_ml = num_red_ml - :num_red_ml,
                                num_green_ml = num_green_ml - :num_green_ml,
                                num_blue_ml = num_blue_ml - :num_blue_ml,
                                num_evil_ml = num_evil_ml - :num_evil_ml
                            """),
            [{"num_red_ml":num_red_ml,"num_green_ml":num_green_ml,"num_blue_ml":num_blue_ml,"num_evil_ml":num_evil_ml}]
        )
    return "OK"

# Gets called 4 times a day
# 
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    # access global_inventory attributes
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
        """
        SELECT num_red_ml, num_green_ml, num_blue_ml, num_evil_ml FROM global_inventory
        """))
        first_row = result.first()
        
    # access potions_table to see what we have/need to be stocked
    with db.engine.begin() as connection:
        pot_table = connection.execute(sqlalchemy.text(
        """
        SELECT * FROM potions_table
        WHERE inventory < 10;
        """))

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    out = []
    barrels = [first_row.num_red_ml,first_row.num_green_ml,first_row.num_blue_ml,first_row.num_evil_ml]

    # checks each row of the potions_table 
    for property in pot_table:

        # stores potion_type and quantity from potions_table
        pot_type = ast.literal_eval(property[2])
        quantity = property[1]
        print(barrels)
        # print("quantity: ", quantity)
        # print("pot_type: ", pot_type)
        
        if quantity < 10:
            if pot_type[0] <= barrels[0] and pot_type[1] <= barrels[1] and pot_type[2] <= barrels[2] and pot_type[3] <= barrels[3]:
                print("pot ", pot_type)
                print("barrels ", barrels)
                result = [a // b if b != 0 else 0 for a, b in zip(pot_type, barrels)]
                if sum(result) != 0:
                    quantity = min([x for x in result if x != 0])
                    out.append(
                    {
                        "potion_type": pot_type,
                        "quantity": quantity
                    }
                    )
                    result = [x * quantity for x in pot_type]
                    # Subtract the second list from the result
                    print(barrels)
                    print(result)
                    barrels = [a - b for a, b in zip(barrels, result)]
                    print(barrels)

        # bottle if possible
            
    return out
