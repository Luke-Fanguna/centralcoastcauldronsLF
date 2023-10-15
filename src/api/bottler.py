import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

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
        result = connection.execute(sqlalchemy.text(
        """
        SELECT num_red_ml, num_red_potions, num_green_ml, num_green_potions, num_blue_ml, num_blue_potions FROM global_inventory
        """))
        first_row = result.first()
    
    print(potions_delivered)
    if len(potions_delivered) != 0:
        red_ml,red_pots = 0,0
        green_ml,green_pots = 0,0
        blue_ml,blue_pots = 0,0
        for potion in potions_delivered:
            pots = potion.quantity * 100
            if potion.potion_type == [100,0,0,0]:
                red_pots, red_ml = first_row.num_red_ml // pots, first_row.num_red_ml % pots
            elif potion.potion_type == [0,100,0,0]:
                green_pots, green_ml = first_row.num_green_ml // pots, first_row.num_green_ml % pots
            elif potion.potion_type == [0,0,100,0]:
                blue_pots, blue_ml = first_row.num_blue_ml // pots, first_row.num_blue_ml % pots

            
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text("""
            UPDATE global_inventory
            SET
                num_red_potions = :red_pots,
                num_red_ml = :red_ml,
                num_green_potions = :green_pots,
                num_green_ml = :green_ml,
                num_blue_potions = :blue_pots,
                num_blue_ml = :blue_ml
                                            """
            ),[{"red_ml" : red_ml,"red_pots" : red_pots,"green_ml" : green_ml,"green_pots" : green_pots,"blue_ml" : blue_ml,"blue_pots" : blue_pots}])
            connection.execute(sqlalchemy.text("""
            UPDATE potions_table
            SET
                quantity = :red_pots
            WHERE sku = 'R_POT';                 
            """),[{"red_pots" : red_pots}])
            connection.execute(sqlalchemy.text("""
            UPDATE potions_table
            SET
                quantity = :green_pots
            WHERE sku = 'G_POT';                 
            """),[{"green_pots" : green_pots}])
            connection.execute(sqlalchemy.text("""
            UPDATE potions_table
            SET
                quantity = :blue_pots
            WHERE sku = 'B_POT';                 
            """),[{"blue_pots" : blue_pots}])

    
        
    return "OK"

# Gets called 4 times a day
# 
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
        """
        SELECT num_red_ml, num_red_potions, num_green_ml, num_green_potions, num_blue_ml, num_blue_potions FROM global_inventory
        """))
        first_row = result.first()
        
    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    poss_barrel = [first_row.num_red_ml,first_row.num_green_ml,first_row.num_blue_ml]
    pot_type = [[100,0,0,0],[0,100,0,0],[0,0,100,0]]
    out = []
    c = 0
    print(poss_barrel)
    for pot in poss_barrel:
        pots = 0
        if (pot >= 100):
            pots = pot // 100
            out.append(
                {
                    "potion_type": pot_type[c],
                    "quantity": pots
                }
            )
        c+=1
            
    print(out)
    
    return out
