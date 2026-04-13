# Springer Capital - Customer Data Pipeline

A robust data pipeline project designed to ingest customer data from a mock API into a PostgreSQL database using `dlt` (Data Load Tool), with a FastAPI service for data access.

## 🚀 Overview

This project consists of three main components:
1.  **Mock Server**: A Flask-based API that serves customer data from a static JSON file with pagination support.
2.  **Pipeline Service**: A FastAPI-based service that handles data ingestion logic using `dlt` and provides endpoints to query the ingested database.
3.  **PostgreSQL**: The destination database for all ingested customer records.

## 🛠️ Tech Stack

*   **Backend**: Python (FastAPI, Flask)
*   **Data Ingestion**: `dlt` (Data Load Tool)
*   **Database**: PostgreSQL
*   **ORM**: SQLAlchemy
*   **Deployment**: Docker & Docker Compose

## 📂 Project Structure

```bash
.
├── mock-server/           # Flask API providing mock customer data
│   ├── data/              # Source JSON data
│   ├── app.py             # Server logic
│   └── Dockerfile
├── pipeline-service/      # FastAPI service & Data Pipeline
│   ├── models/            # SQLAlchemy database models
│   ├── services/          # Data ingestion (dlt) logic
│   ├── main.py            # API endpoints
│   ├── database.py        # Database configuration
│   └── Dockerfile
└── docker-compose.yml     # Orchestration for all services
```

## 🚦 Getting Started

### Prerequisites

*   Docker and Docker Compose installed on your machine.

### running the Application

1.  **Clone the repository** (if applicable).
2.  **Start the services** using Docker Compose:
    ```bash
    docker-compose up -d
    ```
3.  The services will be available at:
    *   **Pipeline Service**: `http://localhost:8000`
    *   **Mock Server**: `http://localhost:5000`
    *   **PostgreSQL**: `localhost:5432`

## 🔌 API Endpoints

### Pipeline Service (`:8000`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Health check / Welcome message |
| `POST` | `/api/ingest` | Triggers the `dlt` pipeline to fetch data from Mock Server |
| `GET` | `/api/customers` | List all ingested customers (Paginated) |
| `GET` | `/api/customers/{id}` | Get details for a specific customer |

### Mock Server (`:5000`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/customers` | Source API for customer data (Paginated) |

## ⚙️ Ingestion Logic

The ingestion is handled by `dlt` in `merge` mode, ensuring:
*   **Upserts**: New records are added, and existing records (matched by `customer_id`) are updated.
*   **Atomic Loading**: Data is loaded into PostgreSQL reliably.
*   **Date Transformation**: ISO strings are converted to proper Python `date` and `datetime` objects during ingestion.

## 📝 Note on `records_processed`

During ingestion, the pipeline reports the number of records processed. Due to `dlt`'s resource flattening, each record is counted individually to ensure the count matches the actual number of customers fetched (e.g., 20 records instead of the total number of dictionary keys).