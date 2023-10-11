import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth


router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


class NewCart(BaseModel):
    customer: str

@router.post("/")
def create_cart(new_cart: NewCart):
    
    cart_id = int(new_cart.customer)
    sql = """ 
    UPDATE carts
    SET 
        cart_id = {}
    """.format(cart_id)
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
        first_row = result.first()
    
    return {"cart_id": cart_id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    sql = """
    SELECT item_sku, quantity, cart_item 
    FROM carts
    WHERE cart_id = {};
    """.format(str(cart_id))
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
        first_row = result.first()

    return {
        "item_sku" : first_row.item_sku,
        "quantity" : first_row.quantity,
        "cart_item" : first_row.cart_item
    }


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    sql = """
    UPDATE carts
    SET 
        item_sku = {},
        cart_item = {}
    WHERE
        cart_id = {};
        """.format(item_sku,cart_item,cart_id)
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
        first_row = result.first()
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    sql = """
    SELECT quantity 
    FROM carts
    WHERE cart_id = {}
    """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql))
        first_row = result.first()
        
    tot_pot = first_row.quantity
    tot_paid = int(cart_checkout.payment)
    
    return {"total_potions_bought": tot_pot, "total_gold_paid": tot_paid}
