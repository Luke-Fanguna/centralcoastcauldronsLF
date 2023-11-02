import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    
    with db.engine.begin() as connection:

        potions = connection.execute(sqlalchemy.text(
        """
        SELECT 
            SUM(quantity)
        FROM potions_ledgers
        """
        )).fetchone()[0]
        if potions is None:
            potions = 0
        
        ml = connection.execute(sqlalchemy.text(
        """
        SELECT 
            SUM(red_ml) AS red,
            SUM(green_ml) AS green,
            SUM(blue_ml) AS blue,
            SUM(evil_ml) AS evil
        FROM ml_ledgers
        """
        )).fetchone()
        print(ml)
        if ml[0] is None:
            ml = 0
        else:
            ml = sum(ml)
        
        gold = connection.execute(sqlalchemy.text(
        """
        SELECT
            SUM(gold)
        FROM gold_ledgers
        """
        )).fetchone()[0]

    print("potions", potions)
    print("ml",ml)
    print("gold",gold)

    return {"number_of_potions": potions, "ml_in_barrels": ml, "gold": gold}
    

class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    print(audit_explanation)
    
    return "OK"
