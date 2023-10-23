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
      result = connection.execute(sqlalchemy.text("""
      SELECT * FROM potions_table
      """))

    catalog = []

    for i in result:
      if i[1] != 0:
        catalog.append(
        {
          "sku" : i[3],
          "name" : i[5],
          "quantity" : i[1],
          "price" : i[4],
          "potion_type" : ast.literal_eval(i[2])
        })
    
    with db.engine.begin() as connection:
      connection.execute(sqlalchemy.text(
        """
            INSERT INTO ledger_log
            (description)
            VALUES
            ('/catalog called\n:catalog');
        """
        ),{"catalog":catalog})
    # Can return a max of 20 items.
    return catalog
