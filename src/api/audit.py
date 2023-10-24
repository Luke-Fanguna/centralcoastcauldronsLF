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


router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    
    potions,ml,gold = 0,0,0
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
        SELECT num_red_ml,num_green_ml,num_blue_ml,num_evil_ml FROM global_inventory
        """))
        for i in result:
            ml = sum(i)
        result = connection.execute(sqlalchemy.text("""
        SELECT inventory FROM potions_table
        """))
        for i in result:
            potions += i[0]
        result = connection.execute(sqlalchemy.text("""
        SELECT gold FROM global_inventory
        """))
        for i in result:
            gold = i[0]
        connection.execute(sqlalchemy.text(
            """
            INSERT INTO ledger_log
            (description)
            VALUES
            ('/inventory:\n potion = :potions\n ml = :ml\n, gold = :gold');
            """    
            ),[{"potions": potions, "ml": ml, "gold": gold}])
    
    return {"number_of_potions": potions, "ml_in_barrels": ml, "gold": gold}

class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    with db.engine.begin as connection:
        connection.execute(sqlalchemy.text(
        """
            INSERT INTO ledger_log
            (description)
            VALUES
            ('/results called');
        """
        ))
    print(audit_explanation)
    
    return "OK"
