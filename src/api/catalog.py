import sqlalchemy
from src import database as db
from fastapi import APIRouter
import ast
# goal: how many potions do we currently have
            
router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
  """
  Each unique item combination must have only a single price.
  """
  with db.engine.begin() as connection:
    potions = connection.execute(sqlalchemy.text(
      """
      SELECT DISTINCT 
        potion_id
      FROM potions_ledgers
      """
    )).fetchall()
    potions = [x[0] for x in potions]

  catalog = []
  for id in potions:
    with db.engine.begin() as connection:
      quantity = connection.execute(sqlalchemy.text(
      """
      SELECT
        SUM(quantity)
      FROM potions_ledgers
      WHERE potion_id = :id;
      """
      ),[{"id":id}]).fetchone()[0]
      if quantity == None:
        quantity = 0
      if quantity > 0:
        potion_name = connection.execute(sqlalchemy.text(
        """
        SELECT
          sku, name, cost, type
        FROM potions_table
        WHERE id = :id
        ORDER BY sku, name, cost, type;
        """
        ),[{"id":id}]).fetchone()
        catalog.append(
          {
            "sku" : potion_name[0],
            "name" : potion_name[1],
            "quantity" : quantity,
            "price":potion_name[2],
            "potion_type" : potion_name[3]
          }
        )

    # Can return a max of 20 items.
  return catalog
