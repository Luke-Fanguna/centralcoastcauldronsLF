import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

customer = ""
cart_id = 0
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
    global cart_id,customer
    cart_id += 1
    customer = new_cart.customer
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text("""
            INSERT INTO carts 
            (cart_id, customer)
            VALUES
            (:cart_id, :customer)
            """),[{"cart_id" : cart_id, "customer" : customer}])
    return {"cart_id": cart_id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):

    cart = []
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
            SELECT * FROM carts
            WHERE cart_id = :cart_id;
            """),[{"cart_id" : cart_id}])
    for i in result:
        cart.append({
            "sku" : i[3],
            "quantity" : i[4]
        })
    return cart


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
        """
        SELECT sku, customer FROM carts
        WHERE cart_id = :cart_id;
        """
        ),[{"cart_id" : cart_id}])
        
        for contents in result: 

            cond = contents[0]
            name = contents[1]

        if cond is None:
            print("new")
            connection.execute(sqlalchemy.text(
            """
            UPDATE carts
            SET
                quantity = :quantity,
                sku = :sku
            WHERE cart_id = :cart_id AND customer = :customer;
            """
            ),[{"quantity" : cart_item.quantity, "cart_id" : cart_id, "sku" : item_sku, "customer" : name}])
        else:
            print("old")
            connection.execute(sqlalchemy.text(
            """
            UPDATE carts
            SET
                quantity = :quantity
            WHERE cart_id = :cart_id AND sku = :sku AND customer = :customer;
            """
            ),[{"quantity" : cart_item.quantity, "cart_id" : cart_id, "sku" : item_sku, "customer" : name}] )
                
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT * FROM carts
            WHERE cart_id = :cart_id;
            """
            ),[{"cart_id":cart_id}])

        for i in result:
            print(i)
            sku = i[3]
            quantity = i[4]
            
        cost = connection.execute(sqlalchemy.text("""
            SELECT cost FROM potions_table
            WHERE sku = :sku;
            """
            ),[{"sku" : sku}])
        
        connection.execute(sqlalchemy.text("""
            UPDATE potions_table
            
            WHERE sku = :sku;
            """
            ),[{"sku" : sku}])
        for val in cost:
            price = val[0]
        print(cart_checkout.payment)
    return {"total_potions_bought": quantity, "total_gold_paid": price * quantity}