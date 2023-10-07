import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math

sql = """
SELECT num_red_ml, num_red_potions, gold FROM global_inventory
"""

with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(sql))
            first_row = result.first()

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    """ """
    print("hello")  
    return {"number_of_potions": 0, "ml_in_barrels": 0, "gold": 0}

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
