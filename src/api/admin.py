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
        TRUNCATE TABLE ml_ledgers, carts_table, gold_ledgers, potions_ledgers CASCADE;
        """
        ))
    return "OK"


@router.get("/shop_info/")
def get_shop_info():

    return {
        "shop_name": "Poly Potions",
        "shop_owner": "Luke Fanguna"
    }

