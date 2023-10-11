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
    potions = f.num_red_potions + f.num_green_potions + f.num_blue_potions
    ml = f.num_red_ml + f.num_green_ml + f.num_blue_ml
    gold = f.gold
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
