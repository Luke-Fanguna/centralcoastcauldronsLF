import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

sql = """
SELECT num_red_potions, gold FROM global_inventory
"""

cart = {}

with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
        first_row = result.first()
        potions = first_row.num_red_potions
        gold = first_row.gold

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


class NewCart(BaseModel):
    customer: str

@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    cart_id = int(new_cart.customer)
    cart[cart_id] = {}
    return {"cart_id": cart_id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    return {}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    cart[cart_id][item_sku] = cart_item.quantity
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    tot_pot = 0
    tot_paid = 0
    if potions != 0:
        for items in cart[cart_id]:
            tot_pot += cart[cart_id][items] 
        tot_paid = int(cart_checkout.payment)
    
    sql = """
        UPDATE global_inventory
        SET 
            num_red_potions = {},
            gold = {}
        WHERE id = 0;
    """.format(potions - tot_pot,gold + tot_paid)
    
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(sql))
    
    return {"total_potions_bought": tot_pot, "total_gold_paid": tot_paid}
