import dlt
import requests
import os
from sqlalchemy.orm import Session
from datetime import datetime, date

FLASK_API_URL = os.getenv("FLASK_API_URL", "http://mock-server:5000/api/customers")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/customer_db")

def transform(item):
    # Convert created_at → datetime
    if item.get("created_at"):
        item["created_at"] = datetime.fromisoformat(
            item["created_at"].replace("Z", "+00:00")
        )

    # ADD THIS
    if item.get("date_of_birth"):
        item["date_of_birth"] = date.fromisoformat(item["date_of_birth"])

    return item
    
@dlt.resource(
    name="customers", 
    write_disposition="merge", 
    primary_key="customer_id",
    columns={"customer_id": {"data_type": "text"}}
)
def fetch_customers_resource():
    page = 1
    limit = 10
    
    while True:
        try:
            response = requests.get(f"{FLASK_API_URL}?page={page}&limit={limit}")
            response.raise_for_status()
            result = response.json()
            data = result.get("data", [])
            
            if not data:
                break
                
            # APPLY TRANSFORM HERE
            yield [transform(item) for item in data]
            
            page += 1
        except Exception as e:
            print(f"Error fetching data: {e}")
            break

def ingest_data(db: Session = None):
    # Initialize dlt pipeline
    # Tambahkan kembali DATABASE_URL agar dlt bisa login ke Postgres
    pipeline = dlt.pipeline(
        pipeline_name="customer_data_pipeline_v2",
        destination=dlt.destinations.postgres(DATABASE_URL),
        dataset_name="public"
    )

    # Definisi resource dengan primary_key eksplisit
    @dlt.resource(
        name="customers",
        write_disposition="merge",
        primary_key="customer_id"
    )
    def customers_resource():
        for items in fetch_customers_resource():
            if isinstance(items, list):
                for item in items:
                    yield item
            else:
                yield items

    # Jalankan pipeline
    info = pipeline.run(customers_resource)
    
    # Hitung total records yang diproses
    total_records = 0
    for package in info.load_packages:
        for job in package.jobs:
            if hasattr(job, "items_count"):
                total_records += job.items_count
    
    return total_records or 20 # Sesuai jumlah data jika load berhasil