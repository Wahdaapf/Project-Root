from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from services.ingestion import ingest_data
from models.customer import Customer

app = FastAPI()

# Create table automatically
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Pipeline Service Running"}


# Data Ingestion Endpoint
@app.post("/api/ingest")
def ingest(db: Session = Depends(get_db)):
    total = ingest_data(db)
    return {
        "status": "success",
        "records_processed": total
    }

def serialize(customer):
    return {
        "customer_id": customer.customer_id,
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "email": customer.email,
        "phone": customer.phone,
        "address": customer.address,
        "date_of_birth": str(customer.date_of_birth),
        "account_balance": float(customer.account_balance) if customer.account_balance else 0,
        "created_at": str(customer.created_at)
    }


@app.get("/api/customers")
def get_customers(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    offset = (page - 1) * limit
    customers = db.query(Customer).offset(offset).limit(limit).all()
    total = db.query(Customer).count()
    return {
        "data": [serialize(c) for c in customers],
        "total": total,
        "page": page,
        "limit": limit
    }


@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return serialize(customer)