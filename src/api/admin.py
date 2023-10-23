import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            """
            UPDATE global_inventory
            SET
                gold = 100,
                num_red_ml = 100,
                num_green_ml = 100,
                num_blue_ml = 100,
                num_evil_ml = 100
            WHERE id = 0;           
            """))
        connection.execute(sqlalchemy.text(
            """
            DELETE FROM carts_table        
            """))
        connection.execute(sqlalchemy.text(
            """
            UPDATE potions_table
            SET
                inventory = 0;
            """))
        connection.execute(sqlalchemy.text(
            """
            INSERT INTO ledger_log
            (description)
            VALUES
            ('reset has been initiated');
            """    
            ))
    return "OK"


@router.get("/shop_info/")
def get_shop_info():

    return {
        "shop_name": "Poly Potions",
        "shop_owner": "Luke Fanguna"
    }

