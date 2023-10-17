import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math

sql = """
        SELECT *
        FROM global_inventory
        """

with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(sql))
            f = result.first()

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    
    print("hello")  
    potions,ml,gold = 0,0,0
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
        SELECT num_red_ml,num_green_ml,num_blue_ml,num_evil_ml FROM global_inventory
        """))
        for i in result:
            ml = sum(i)
        result = connection.execute(sqlalchemy.text("""
        SELECT num_red_potions,num_green_potions,num_blue_potions,num_evil_potions FROM global_inventory
        """))
        for i in result:
            potions = sum(i)
        result = connection.execute(sqlalchemy.text("""
        SELECT gold FROM global_inventory
        """))
        for i in result:
            gold = i[0]
    
    return {"number_of_potions": potions, "ml_in_barrels": ml, "gold": gold}

class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    """ """
    print(audit_explanation)
    
    return "OK"
