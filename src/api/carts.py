import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum

customer = ""
cart_id = 0
router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


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
        connection.execute(sqlalchemy.text(
        """
            INSERT INTO ledger_log
            (description)
            VALUES
            ('/carts/ called\n created cart for :customer \n id: :id');
        """
        ),[{"customer":new_cart.customer,"id":id}])

    

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
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
        """
            INSERT INTO ledger_log
            (description)
            VALUES
            ('/carts/(get) called\n created cart for :customer \n id: :id \n cart:\n :cart');
        """
        ),[{"cart":cart}])
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
        
        connection.execute(sqlalchemy.text(
        """
            INSERT INTO ledger_log
            (description)
            VALUES
            ('/carts/(add) called\n added :sku quantity :quantity for cart_id :cart_id');
        """
        ),[{"sku":item_sku, "quantity":cart_item.quantity, "cart_id":cart_id}])
        
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
            
            connection.execute(sqlalchemy.text(
            """
            UPDATE carts_items_table
            SET is_check = true
            WHERE cart_id = :id
            """
            ),[{"id":cart_id}]) 
        
        connection.execute(sqlalchemy.text(
        """
            INSERT INTO ledger_log
            (description)
            VALUES
            ('/carts/checkout called\ncheckout intitiated\ncustomer (:cart_id) got :potions potions and spent :gold');
        """
        ),{"cart_id":cart_id,"potions":quantity,"gold":price})
        
        print(cart_checkout.payment)
        return {"total_potions_bought": quantity, "total_gold_paid": price}
    connection.execute(sqlalchemy.text(
        """
            INSERT INTO ledger_log
            (description)
            VALUES
            ('/carts/checkout called\ncheckout calld again. do nothing');
        """
        ),{"cart_id":cart_id,"potions":quantity,"gold":price})
    return {}