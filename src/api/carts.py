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
        (cart_id, potions_id, quantity, is_check)
        VALUES
        (:cart_id, :potions_id, :quantity, false);
        """
        ),[{"cart_id" : cart_id, "potions_id" : potions_id, "quantity" : cart_item.quantity}])
        
        
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    cond = False
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
        """
        SELECT is_check FROM carts_items_table
        WHERE id = :id;
        """
        ),[{"id":cart_id}])
        for i in result:
            cond = i[0]
            
    if not cond:
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
                print(i)
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
                connection.execute(sqlalchemy.text("""
                UPDATE potions_table
                SET
                    inventory = inventory - :inventory
                WHERE sku = :sku
                """),[{"inventory" : i[3],"sku": i[8]}])
                quantity += i[3]
                
                price += (i[3] * i[9])
            
            connection.execute(sqlalchemy.text(
            """
            UPDATE global_inventory
            SET
                gold = gold + :gold
            """), [{"gold" : price}])
            
            
            result = connection.execute(sqlalchemy.text(
            """
            SELECT customer FROM carts_table
            WHERE id = :id
            """),[{"id":cart_id}]
            )
            for i in result:
                name = i[0]
            
            acc_id = connection.execute(sqlalchemy.text(
            """
            INSERT INTO accounts (account_name) VALUES (:name)
            RETURNING id;
            """
            ),[{"name":name}])
            
            acc_t_id = connection.execute(sqlalchemy.text(
            """
            INSERT INTO account_transactions (description) VALUES (:description)
            RETURNING id;
            """
            ),[{"description":"{} paid {} and bought {} potions and paid with {}".format(name,price,quantity,cart_checkout.payment)}])
            
            for i in acc_id:
                accounts_id = i[0]
            for i in acc_t_id:
                accounts_t_id = i[0]
            
            connection.execute(sqlalchemy.text(
            """
            INSERT INTO account_ledger_entries (account_id,account_transaction_id,change)
            VALUES (:account_id,:account_transaction,:change);
            """
            ),[{"account_id":accounts_id,"account_transaction":accounts_t_id,"change":price}])   
            
            connection.execute(sqlalchemy.text(
            """
            UPDATE carts_items_table
            SET is_check = true
            WHERE cart_id = :id
            """
            ),[{"id":cart_id}]) 
            
        print(cart_checkout.payment)
        return {"total_potions_bought": quantity, "total_gold_paid": price}
    return {}