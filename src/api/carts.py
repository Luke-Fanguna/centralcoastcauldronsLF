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

    with db.engine.begin() as connection:
        cart_id = connection.execute(
            sqlalchemy.text("""
            INSERT INTO carts_table
            (customer)
            VALUES
            (:customer)
            RETURNING id
            """),[{"customer" : new_cart.customer}])

    for i in cart_id:
        id = i[0]

    return {"cart_id": id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):

    cart = []

    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
            SELECT * FROM carts_items_table
            WHERE cart_id = :cart_id;
            """),[{"cart_id" : cart_id}])
        
    for i in result:
        quantity = i[3]
        with db.engine.begin() as connection:
            a = connection.execute(sqlalchemy.text("""
            SELECT sku FROM potions_table
            WHERE id = :id
            """),[{"id" : i[2]}])
        for x in a:
            print(x)
            id = x[0]
            
    cart.append({
        "sku" : id,
        "quantity" : quantity
    })
    return cart


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):


    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
        """
        SELECT id FROM potions_table
        WHERE sku = :sku;
        """
        ),[{"sku" : item_sku}])
        
        potions_id = [i[0] for i in result][0]
        
        connection.execute(sqlalchemy.text(
        """
        INSERT INTO carts_items_table
        (cart_id, potions_id,quantity)
        VALUES
        (:cart_id,:potions_id,:quantity)
        """
        ),[{"cart_id" : cart_id, "potions_id" : potions_id, "quantity" : cart_item.quantity}])
        
        
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
        """
        WITH filtered_table as
        (
            SELECT * FROM carts_items_table
            WHERE cart_id = :cart_id
        )
        SELECT *
        FROM filtered_table
        INNER JOIN potions_table ON filtered_table.potions_id = potions_table.id;
        """
            ),[{"cart_id":cart_id}])
        
        price, quantity = 0,0
        for i in result: 
            # 0 carts_items_table.id, 
            # 1 carts_table.id, 
            # 2 potions_table.id, 
            # 3 carts_items_table.quantity, 
            # 4 carts_table.potion_id, 
            # 5 potions_table.quantity, 
            # 6 potions_table.potion_type, 
            # 7 potions_table.sku, 
            # 8 potions_table.cost, 
            # 9 potions_table.name
            print(i)
            connection.execute(sqlalchemy.text("""
            UPDATE potions_table
            SET
                inventory = inventory - :inventory
            WHERE sku = :sku
            """),[{"inventory" : i[3],"sku": i[7]}])
            quantity += i[3]
            price += (i[3] * i[8])
        connection.execute(sqlalchemy.text(
            """
            UPDATE global_inventory
            SET
                gold = :gold
            """), [{"gold" : price}])
    return {"total_potions_bought": quantity, "total_gold_paid": price}