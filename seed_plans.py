import app.models 

from app.db.session import SessionLocal
from app.models.plan import Plan


db = SessionLocal()


free_plan = Plan(

    name="free",
    
    price=0,

    limits={

        "max_concurrent_runs": 1

    }
)


db.add(free_plan)

db.commit()

print("Free plan created successfully")