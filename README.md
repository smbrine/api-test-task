# api-test-task

## Introduction
A simple FastAPI service for calculating cargo insurance costs.

---

## Quick Start

### Installation

#### Option 1: Local Setup

1. **Install dependencies**  
   Choose your preferred method to install the dependencies:

   - **Using Poetry (Recommended):**
     ```bash
     poetry install
     ```
   - **Using pip:**
     ```bash
     pip install -r requirements.txt
     ```

2. **Start PostgreSQL**  
   You can use Docker Compose or any other method to start a PostgreSQL instance:

   - **Using Docker Compose:**
     ```bash
     docker compose -f deploy/docker-compose.yml run postgres -d --no-deps --remove-orphans
     ```

3. **Configure PostgreSQL Endpoint**  
   Update the `.env` file to point to the correct PostgreSQL endpoint.

4. **Apply Database Migrations**  
   Run the following command to apply the migrations:
   ```bash
   alembic upgrade head
   ```

5. **[Optional] Generate a Test Dataset**  
   To generate and upload test rates, run:
   ```bash
   python -m app.main \
     --generate-rates \
     --upload-rates \
     --exit-on-upload \
     --generate-rates-from 2023-01-01
   ```

6. **Run the Application**  
   Start the application with:
   ```bash
   python -m app.main --upload-rates
   ```