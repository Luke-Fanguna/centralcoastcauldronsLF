import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import ast
import json
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
    print(potions_delivered)
    with db.engine.begin() as connection:
        
        # additional_potions = sum(potion.quantity for potion in potions_delivered)
        num_red_ml = sum(potion.quantity * potion.potion_type[0] for potion in potions_delivered)
        num_green_ml = sum(potion.quantity * potion.potion_type[1] for potion in potions_delivered)
        num_blue_ml = sum(potion.quantity * potion.potion_type[2] for potion in potions_delivered)
        num_evil_ml = sum(potion.quantity * potion.potion_type[3] for potion in potions_delivered)


        
        for potion_delivered in potions_delivered:
            id = connection.execute(sqlalchemy.text(
            """
            SELECT id
            FROM potions_table
            WHERE type = :type
            """),
            [{"type":str(potion_delivered.potion_type)}]).fetchone()[0]
            connection.execute(sqlalchemy.text(
            """
            INSERT INTO potions_ledgers
            (potion_id,quantity)
            VALUES
            (:potion_id,:quantity)
            """
            ),[{"potion_id":id,"quantity":potion_delivered.quantity}])

        connection.execute(sqlalchemy.text(
        """
        INSERT INTO ml_ledgers
        (red_ml,green_ml,blue_ml,evil_ml)
        VALUES
        (:red_ml,:green_ml,:blue_ml,:evil_ml)
        """
        ),
        [{"red_ml":-num_red_ml,"green_ml":-num_green_ml,
          "blue_ml":-num_blue_ml,"evil_ml":-num_evil_ml}])
        
            
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
        barrels = connection.execute(sqlalchemy.text(
        """
        SELECT 
            SUM(red_ml) AS red_ml, 
            SUM(green_ml) AS green_ml,
            SUM(blue_ml) AS blue_ml, 
            SUM(evil_ml) AS evil_ml
        FROM ml_ledgers
        ORDER BY red_ml, green_ml, blue_ml, evil_ml
        """)).fetchone()
        barrels = list(barrels)
        
    # access potions_table to see what we have/need to be stocked
    with db.engine.begin() as connection:
        pot_table = connection.execute(sqlalchemy.text(
        """
        SELECT type 
        FROM potions_table
        """)).fetchall()
    pot_table = [list(ast.literal_eval(x[0])) for x in pot_table]

    out = []
    possible = True
    while possible:
        for pot_type in pot_table:
            print("potion type:",pot_type)        
            print("barrels:",barrels)
            if pot_type[0] <= barrels[0] and pot_type[1] <= barrels[1] and pot_type[2] <= barrels[2] and pot_type[3] <= barrels[3]:
                found = False
                for entry in out:
                    if entry["potion_type"] == pot_type:
                        entry["quantity"] += 1
                        found = True
                        break
                if not found:
                    out.append({
                        "potion_type": pot_type,
                        "quantity": 1
                    })
                barrels = [x - y for x, y in zip(barrels, pot_type)]
            else:
                possible = False
    json_string = json.dumps(out, indent=4)
    print(json_string)
    return out
