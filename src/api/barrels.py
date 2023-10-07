import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

#goal: can only sell a barrel if total number of potions is less than 10

sql = """
    SELECT gold, num_red_ml, num_red_potions FROM global_inventory
    """

with db.engine.begin() as connection:
    result = connection.execute(sqlalchemy.text(sql))
    first_row = result.first()


router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print(barrels_delivered)

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    
    print(wholesale_catalog)
    
    # sku = ""
    # min_price = wholesale_catalog[0]
    quantity = 0
    # barrel = wholesale_catalog[0]

    # for i in range(1,wholesale_catalog):
    #     print(sku)
    #     if min_price < wholesale_catalog[i].price:
    #         sku = wholesale_catalog[i].sku
    #         quantity = wholesale_catalog[i].quantity
    #         barrel = wholesale_catalog[i]

    # ml = barrel.ml_per_barrel * barrel.quantity

    
    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": quantity
        }
    ]
