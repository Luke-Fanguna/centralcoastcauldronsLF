import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
from datetime import datetime

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
    with db.engine.begin() as connection:
        if customer_name != "" and potion_sku != "":
            print("customer name:",customer)
            print("potion_sku:",potion_sku)
            potion_id = connection.execute(sqlalchemy.text(    
            """
            SELECT 
                id
            FROM potions_table
            WHERE sku = :sku
            """
            ),[{"sku":potion_sku}]).scalar_one()

            cust_id = connection.execute(sqlalchemy.text(
            """
            SELECT
                id
            FROM carts_table
            WHERE customer = :customer
            """
            ),[{"customer":customer_name}]).scalar_one()
            
            info = connection.execute(sqlalchemy.text(
            """
            SELECT
                customer.customer AS name,
                cart.quantity AS quantity,
                potions.name AS potion_name,
                potions.cost AS cost,
                cart.created_at AS timestamp
            FROM carts_items_table AS cart
            INNER JOIN carts_table AS customer ON cart.cart_id = customer.id
            INNER JOIN potions_table AS potions ON cart.potions_id = potions.id
            WHERE customer.id = :cart_id AND potions.id = :potions_id
            ORDER BY name, quantity, cost, potion_name, timestamp;
            """
            ),[{"potions_id":potion_id,"cart_id":cust_id}]).fetchall()
        elif customer_name != "" and potion_sku == "":
            print("customer name:",customer)
            print("potion_sku:",potion_sku)
            cust_id = connection.execute(sqlalchemy.text(
            """
            SELECT
                id
            FROM carts_table
            WHERE customer = :customer
            """
            ),[{"customer":customer_name}]).scalar_one()
            
            info = connection.execute(sqlalchemy.text(
            """
            SELECT
                customer.customer AS name,
                cart.quantity AS quantity,
                potions.name AS potion_name,
                potions.cost AS cost,
                cart.created_at AS timestamp
            FROM carts_items_table AS cart
            INNER JOIN carts_table AS customer ON cart.cart_id = customer.id
            INNER JOIN potions_table AS potions ON cart.potions_id = potions.id
            WHERE customer.id = :cart_id
            ORDER BY name, quantity, cost, potion_name, timestamp;
            """
            ),[{"cart_id":cust_id}]).fetchall()
        elif customer == "" and potion_sku != "":
            print("customer name:",customer)
            print("potion_sku:",potion_sku)
            potion_id = connection.execute(sqlalchemy.text(    
            """
            SELECT 
                id
            FROM potions_table
            WHERE sku = :sku
            """
            ),[{"sku":potion_sku}]).scalar_one()
            
            info = connection.execute(sqlalchemy.text(
            """
            SELECT
                customer.customer AS name,
                cart.quantity AS quantity,
                potions.name AS potion_name,
                potions.cost AS cost,
                cart.created_at AS timestamp
            FROM carts_items_table AS cart
            INNER JOIN carts_table AS customer ON cart.cart_id = customer.id
            INNER JOIN potions_table AS potions ON cart.potions_id = potions.id
            WHERE potions.id = :potions_id
            ORDER BY name, quantity, cost, potion_name, timestamp;
            """
            ),[{"potions_id":potion_id}]).fetchall()
        else:
            print("customer name:",customer)
            print("potion_sku:",potion_sku)
            info = connection.execute(sqlalchemy.text(
            """
            SELECT
                customer.customer AS name,
                cart.quantity AS quantity,
                potions.name AS potion_name,
                potions.cost AS cost,
                cart.created_at AS timestamp
            FROM carts_items_table AS cart
            INNER JOIN carts_table AS customer ON cart.cart_id = customer.id
            INNER JOIN potions_table AS potions ON cart.potions_id = potions.id
            ORDER BY name, quantity, cost, potion_name, timestamp;
            """
            )).fetchall()
        print(info)
        if sort_col == "customer_name":
            info = sorted(info, key=lambda x: x[0])
        elif sort_col == "item_sku":
            info = sorted(info, key=lambda x: x[2])
        elif sort_col == "line_item_total":
            info = sorted(info, key=lambda x: x[3])
        elif sort_col == "timestamp":
            info = sorted(info, key=lambda x: x[4])
        
        if sort_order == "desc":
            info.reverse()
        
        if search_page == '':
            search_page = 1
        
        n = int(search_page) * 5
            
        if len(info) > n:
            a = n - 5
            b = n
        else:
            a = n - 5
            b = len(info)
        out = []
        # customer, q, name, price, time
        for i in range(a,b):
            print(info[i])
            time = info[i][4].strftime("%m/%d/%Y, %I:%M:%S %p")
            out.append([{
                "line_item_id":i+1,                      
                "item_sku":str(info[i][1]) + " " + str(info[i][2]),
                "customer_name":info[i][0],              
                "line_item_total":info[i][3] * info[i][1],
                "timestamp":time,
                }
                ])
        if int(search_page) == 1:
            prev = ""
            next = "2"
        else:
            prev = str(int(search_page) - 1)
            next = str(int(search_page) + 1)
        return {
        "previous": prev,
        "next": next,
        "results": out
        }


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
            """),[{"customer" : new_cart.customer}]).fetchone()[0]
    return {"cart_id": cart_id}


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
            id = connection.execute(sqlalchemy.text("""
            SELECT sku FROM potions_table
            WHERE id = :id
            """),[{"id" : i[2]}]).fetchone()[0]
            
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
        SELECT id, cost FROM potions_table
        WHERE sku = :sku
        ORDER BY id, cost;
        """
        ),[{"sku" : item_sku}])
        
        potions_id = result[0]
        cost = result[1]
        
        connection.execute(sqlalchemy.text(
        """
        INSERT INTO carts_items_table
        (cart_id, potions_id, quantity, total, is_check)
        VALUES
        (:cart_id, :potions_id, :quantity, :cost * :quantity, false);
        """
        ),[{"cart_id" : cart_id, "potions_id" : potions_id,"cost":cost, "quantity" : cart_item.quantity}])
              
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
                SELECT potions_id FROM carts_items_table
                WHERE cart_id = :cart_id
            )
            SELECT 
                potions_table.sku,
                potions_table.cost,
                potions_table.id
            FROM filtered_table
            INNER JOIN potions_table ON filtered_table.potions_id = potions_table.id
            ORDER BY potions_table.sku, potions_table.cost, potions_table.id;            
            """
                ),[{"cart_id":cart_id}]).fetchone()
            
            print(result)
                        
            quantity = connection.execute(sqlalchemy.text("""
            SELECT 
                sum(quantity)
            FROM potions_ledgers
            WHERE potion_id = :id
            """),[{"id":result[2]}]).fetchone()[0]

            connection.execute(sqlalchemy.text(
            """
            INSERT INTO potions_ledgers
            (potion_id,quantity)
            VALUES
            (:id,:quantity)                                    
            """),[{"id":id,"quantity":-quantity}])
            
            price = result[1] * quantity
            connection.execute(sqlalchemy.text(
            """
            INSERT INTO gold_ledgers
            (gold)
            VALUES
            (:gold);
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
        
            return {"total_potions_bought": quantity, "total_gold_paid": price}
    return {}