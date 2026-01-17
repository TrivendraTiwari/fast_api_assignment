## Task Management System  
## overview 

A robust and scalable Task Management System developed using FastAPI, PostgreSQL, Redis, and Keycloak for secure role-based access control.
This application is optimized for high performance, capable of handling large volumes of requests efficiently by leveraging caching, table partitioning, connection pooling, and scalable deployment strategies.

## Key Features
- User Management & Authentication: Secure login and role handling using **Keycloak** with role-based access control.
- Task Operations: Create, read, update, and delete tasks with full transactional integrity.
- Caching Layer: Frequently accessed API responses cached in **Redis** to improve performance and reduce database load.
- PostgreSQL Backend: Relational database with **Alembic** migrations for schema versioning and smooth upgrades.
- Role-Based Access Control (RBAC): Granular permissions for Admin and User operations.
- Asynchronous Notifications: Automated email notifications sent via **Celery** in the background without blocking API requests.
- Automated Testing: Comprehensive test coverage using **pytest** to validate endpoints and ensure system stability.
- Database Health Monitoring: Exposes **Prometheus metrics** for database connectivity, query latency, and error tracking for proactive monitoring.



## Technology Stack Used
- **Backend Framework:** FastAPI with Python
- **Database:** PostgreSQL
- **Caching Layer:** Redis
- **Authentication & Authorization:** Keycloak (OIDC)
- **ORM:** SQLAlchemy
- **Database Migrations:** Alembic
- **Asynchronous Task Processing:** Celery for background email notifications
- **Monitoring & Metrics:** Prometheus for database health and performance



## Setup Instructions to follow 

1. **Clone git repo**
   ```bash
   git clone https://github.com/TrivendraTiwari/fast_api_assignment.git
   cd project-name

2. **Install dependencies**
pip install -r requirements.txt


3. **Run Redis and Keycloak**
redis-server

4. **Run Keycloak**
kc.bat start-dev

5. **Database Migrations Using Alembic**
After the configurations steps of alembic env files

**Create Migration**  
alembic revision --autogenerate -m "create tables"
**Update Database Migrations**
alembic upgrade head

5. ## RunApplication

**bash**
uvicorn task_app.app.main:app --reload


**Acess the Application at**
http://127.0.0.1:8000


**Api Documentation (Swagger)**:
http://127.0.0.1:8000/docs


## Background Schduler Tasks (Celery for notification service over email)
**command to run celery background process**
celery -A task_app.app.celery_app.celery worker --loglevel=info -P solo


##  **Role Based API Endpoint Urls**


| Method | Endpoint      | Description               | Access       |
| ------ | ------------- | ------------------------- | ------------ |
| POST   | `/tasks`      | Create a new task         | Admin, User  |
| GET    | `/tasks`      | List tasks (paginated)    | Admin, User  |
| GET    | `/tasks/{id}` | Retrieve task by ID       | Admin, User  |
| PATCH  | `/tasks/{id}` | Update task fields        | Admin, User  |
| DELETE | `/tasks/{id}` | Delete a task             | Admin        |
| GET    | `/metrics`    | Expose Prometheus metrics | Admin, User  |


**Health / Metrics Logs (Prometheus)**

| Metric                                  | Type      | Description                                           |
| --------------------------------------- | --------- | ----------------------------------------------------- |
| `python_gc_objects_collected_total`     | counter   | Objects collected by Python GC per generation.        |
| `python_gc_objects_uncollectable_total` | counter   | Objects GC could not collect (possible memory leaks). |
| `python_gc_collections_total`           | counter   | Number of times GC ran per generation.                |
| `python_info`                           | gauge     | Python interpreter info (version, implementation).    |
| `db_up`                                 | gauge     | **Database connectivity status (1 = up, 0 = down).**  |
| `db_query_latency_seconds`              | histogram | DB query latency distribution.                        |
| `db_query_latency_seconds_count`        | counter   | Number of DB queries measured.                        |
| `db_query_latency_seconds_sum`          | counter   | Total time spent on DB queries.                       |
| `db_errors_total`                       | counter   | Total number of DB errors.                            |


**Api Automated testing with pytest**
**run command**
pytest test_tasks.py (path dependent)


**Authentication Technique Used**

This application implements OAuth2-based authentication using JWT tokens issued by Keycloak. The FastAPI backend validates access tokens against the JWKS endpoint, extracts user information (username and roles), and enforces role-based access control for protected endpoints.

Token validation: Uses RS256 signed JWTs verified with Keycloak public keys.

Role-based authorization: Endpoints can restrict access to users with specific roles via a reusable dependency (require_role).

Caching: JWKS keys are cached in memory to reduce network calls.


**For all protected endpoints, include the token in the Authorization header**
Authorization: Bearer <access_token>

**Request to generate the JWT Authorizations token**



curl -X POST "http://localhost:8080/realms/myrealm/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=<myclient>" \
  -d "username=<testuser>" \
  -d "client_secret=<your_client_secret>" \
  -d "password=<yourpassword>" \
  -d "grant_type=password"


**Example Request to List all the tasks created by the user (via curl)**
**Endpoint: GET /tasks**
**Roles allowed: user, admin**
**Rate-Limiting enabled**

  curl -X GET "http://127.0.0.1:8000/tasks" \
  -H "Authorization: Bearer <access_token>"

**Response**
{
    "total": 3,
    "page": 1,
    "page_size": 10,
    "items": [
        {
            "id": "67532b32-62a7-4440-af9e-292b98c3078a",
            "title": "my_new_task1",
            "description": "sdfsg",
            "status": "in_progress"
        },
        {
            "id": "c4c5fa20-e803-4827-a2cf-110562fe7799",
            "title": "my_point_1",
            "description": "sdfsg",
            "status": "completed"
        },
        {
            "id": "c844941e-5d58-49f5-94c3-d500dc9b82e7",
            "title": "my_point_12345678",
            "description": "sdfsg",
            "status": "in_progress"
        }
    ]
}

**Example Request to List all the tasks created by the user (via curl) with pagination**
**Endpoint: GET /tasks**
**Roles allowed: user, admin**
**Rate-Limiting enabled**

curl -X GET "http://127.0.0.1:8000/tasks?page=1&page_size=10" \
-H "Authorization: Bearer <access_token>"


**Example Request to create new task(via curl)**
**Endpoint: POST /tasks**
**Roles allowed: user, admin**
**Rate-Limiting enabled**

curl -X POST "http://127.0.0.1:8000/tasks" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <access_token>" \
-d '{
    "title": "my_new_task",
    "description": "Description of the task",
    "status": "pending"
}'

**Response**

{
    "id": "a3f1c8f2-0b28-4f77-bd4a-123456789abc",
    "title": "my_new_task",
    "description": "Description of the task",
    "status": "pending"
}


**Example Request to get task using existing task id(via curl)**
**Endpoint: GET /tasks/{id}**
**Roles allowed: user, admin**
**Rate-Limiting enabled**

 curl -X GET "http://127.0.0.1:8000/tasks/a3f1c8f2-0b28-4f77-bd4a-123456789abc" \
-H "Authorization: Bearer <access_token>"

**response**
{
    "id": "a3f1c8f2-0b28-4f77-bd4a-123456789abc",
    "title": "my_new_task",
    "description": "Description of the task",
    "status": "pending"
}
**If task not found (404 Not Found)**
{
    "detail": "Task not found"
}


**Example Request to update existing task(via curl)**
**Endpoint: PATCH /tasks/{id}**
**Roles allowed: user, admin**
**Rate-Limiting enabled**

curl -X PATCH "http://127.0.0.1:8000/tasks/a3f1c8f2-0b28-4f77-bd4a-123456789abc" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <access_token>" \
-d '{
    "title": "updated_task_title",
    "status": "completed"
}'

**Response**
{
    "id": "a3f1c8f2-0b28-4f77-bd4a-123456789abc",
    "title": "updated_task_title",
    "description": "Description of the task",
    "status": "completed"
}

**If task not found (404 Not Found)**
{
    "detail": "Task not found"
}

**Example Request to delete existing task(via curl)**
**Endpoint: DELETE /tasks/{id}**
**Roles allowed: admin only**
**Rate-Limiting enabled**

curl -X DELETE "http://127.0.0.1:8000/tasks/a3f1c8f2-0b28-4f77-bd4a-123456789abc" \
-H "Authorization: Bearer <access_token>"

**Response**

<empty response>->No Content

**If task not found (404 Not Found)**
{
    "detail": "Task not found"
}


**Key Features**
1. Connection Pooling

Implements database connection pooling using SQLAlchemy to efficiently reuse connections, enabling high levels of concurrency while preventing connection exhaustion under heavy parallel workloads.


2. Table Partitioning

The primary tasks table is horizontally partitioned into multiple child tables using a hash-based strategy on `user_id`. This approach reduces the size of individual partitions, lowers query scanning overhead, and significantly improves performance when working with large-scale datasets.


3. Redis Caching

High-traffic API endpoints (for example, `GET /tasks`) leverage Redis-based caching to store frequently requested responses. This reduces repeated database queries, lowers overall database load, and improves response latency for repeated requests.


4. Database Indexing

Indexes are applied on frequently queried columns such as `status` and `created_at` to accelerate filtering and search operations, ensuring efficient query execution even as the dataset grows large.


5. Role-Based Access Control (RBAC)

Authentication and authorization are implemented using Keycloak, enabling secure role-based access control. Users are assigned specific roles (such as `user` or `admin`) that govern their permitted API operations based on defined privileges.


6. Scalable Application Workers

The FastAPI application is deployed with multiple Uvicorn worker processes, allowing concurrent request handling and efficient utilization of available CPU cores to achieve higher throughput under load.



7. Asynchronous Email Notification System

- Implemented background email notifications using Celery that trigger when a new task is created.
- Email delivery is handled asynchronously to ensure API responses remain non-blocking and performant.
- Celery is configured with Redis as the message broker for reliable task queue management.

8. Automated API Testing Framework

- All API endpoints are validated using automated tests written with pytest.
- Test cases verify endpoint behavior, input validation, and expected responses to ensure reliability and long-term stability of the API.

9. Rate Limiting

Rate limiting is implemented to control the number of requests a client can make to the API within a defined time window. This mechanism helps protect the system from abuse while ensuring fair usage of resources.

### Implementation Overview
- Requests are rate-limited based on client identity (e.g., user ID or IP address).
- Limits are enforced per time window (for example, requests per minute).
- Redis is used as a centralized store to track request counters efficiently and atomically.
- When a client exceeds the allowed threshold, the API responds with an appropriate HTTP error (e.g., `429 Too Many Requests`).

### Why Rate Limiting Is Important
- Prevents excessive or abusive API usage that can degrade system performance.
- Protects backend services and the database from overload during traffic spikes.
- Ensures fair resource distribution among all users.
- Improves overall system stability and reliability under high load.

### Security Threats Mitigated
Rate limiting helps defend against several common attack vectors, including:
- **Brute-force attacks** – Limits repeated login or credential-guessing attempts.
- **Denial of Service (DoS) attacks** – Reduces the impact of high-volume request floods.
- **Credential stuffing** – Restricts automated attempts using leaked credentials.
- **API abuse and scraping** – Prevents uncontrolled automated access to API endpoints.

By enforcing rate limits, the application maintains consistent performance, improves security posture, and ensures a better experience for legitimate users.


10. Database Health Monitoring with Prometheus

Prometheus is integrated to expose real-time database health metrics, including connectivity status, query latency, and error counts. These metrics enable continuous monitoring, early detection of performance degradation, and proactive alerting for database-related issues.


## Answers Section

### Describe how you would design the application architecture, including database design, API scalability, and authentication setup.

### Application Architecture

#### 1. Overall Design

The application is built using a modular FastAPI-based architecture, integrating PostgreSQL for persistent data storage, Redis for caching, Celery for asynchronous background processing, and Keycloak for secure authentication and authorization.  
ensuring consistent behavior across development, testing, and production environments while supporting scalable deployments.


#### 2. Database Design

PostgreSQL is used as the core relational datastore for the application.  
The primary `tasks` table is horizontally sharded into eight partitions using a hash-based strategy on `user_id`, which helps distribute data evenly, reduces lock contention, and improves query execution on large datasets.  
Strategic indexes are applied on high-selectivity columns such as `status` and `created_at` to optimize filtering and sorting operations.  
Database connection efficiency under concurrent load is maintained through SQLAlchemy’s built-in connection pooling mechanism.


#### 3. API Scalability

The FastAPI service is deployed with multiple Uvicorn worker processes to enable parallel request handling and effective utilization of multi-core CPU environments.  
Redis is integrated as an in-memory cache to serve frequently requested resources, such as task listings, significantly reducing repetitive database queries.  
The architecture supports horizontal scalability by running multiple FastAPI containers behind a load balancer, ensuring fault tolerance and high request throughput.  
Asynchronous workloads, including email notifications triggered on task creation, are offloaded to Celery workers, allowing the core API to remain responsive under load.


#### 4. Authentication & Authorization

User authentication and role-based access control (RBAC) are implemented using Keycloak.  
Users acquire a Bearer token from Keycloak, which is validated by FastAPI for each incoming request.  
API routes are secured with role-based checks (e.g., `admin`, `user`) to enforce access permissions and protect sensitive operations.


#### 5. Email Notification

When a new task is created, a Celery background worker is triggered to deliver an email notification to the creator.  
This asynchronous approach ensures that API response times remain fast and non-blocking.  
SMTP credentials and email templates are securely managed through environment variables to protect sensitive information.



### Explain how you would implement caching (e.g., for frequently accessed tasks) and message queuing (e.g., for background task processing)

#### 1. Caching

Redis is employed to store frequently requested data, such as task listings from `GET /tasks`.  
A **cache-aside pattern** is implemented:  
- Check Redis cache first → if a cache miss occurs, query the database → populate the cache with a short TTL (e.g., 30–60 seconds).  
- Cache entries are invalidated on data-modifying operations (`POST`, `PUT`, `DELETE`) to maintain consistency.  
- Structured cache keys are used for easy retrieval and organization, for example:  


#### 2. Message Queuing

Celery is integrated with a message broker (Redis or RabbitMQ) to handle background tasks.  
Long-running operations, such as sending emails or running analytics, are offloaded to Celery workers.  
Tasks are triggered asynchronously from FastAPI using the `task.delay(args)` method.  
This design ensures that the API remains responsive and performant while background tasks execute independently.



**Provide a diagram of the architecture**

## Architecture Diagram

Below is a proposed architecture for a production-ready FastAPI Task Management System:

                             ┌──────────────┐
                             │   Clients    │ (Web / Mobile / CLI)
                             └──────┬───────┘
                                    │ HTTPS / REST
                                    ▼
                            ┌──────────────────┐
                            │ Load Balancer    │ (NGINX / Traefik / Cloud LB)
                            └──────┬───────────┘
                                   │
                ┌──────────────────┼───────────────────┐
                ▼                  ▼                   ▼
         ┌────────────┐      ┌────────────┐      ┌────────────┐
         │ FastAPI    │      │ FastAPI    │      │ FastAPI    │
         │ (Uvicorn)  │      │ (Uvicorn)  │  →   │ (Uvicorn)  │  ← multiple replicas
         └────┬───────┘      └────┬───────┘      └────┬───────┘
              │                    │                  │
      ┌───────┴─────────┐          │          ┌───────┴─────────┐
      │ Redis Cache     │          │          │ Celery Workers   │
      │ (Hot tasks, TTL)│          │          │ Background Jobs  │
      └───────┬─────────┘          │          └────────┬────────┘
              │                    │                   │
        ┌─────▼─────┐        ┌─────▼─────┐        ┌────▼─────┐
        │ PostgreSQL │        │ PostgreSQL│        │ Message   │
        │ Primary    │        │ Read Rep. │        │ Broker    │
        │ (Partitioned tasks)  │           │        │ (Redis / RabbitMQ) │
        └─────┬─────┘        └─────┬─────┘        └─────┬─────┘
              │                    │                   │
      ┌───────▼────────┐    ┌─────▼─────────┐         │
      │ Prometheus     │    │ Grafana       │         │
      │ DB Metrics     │    │ Dashboard     │         │
      │ (latency,      │    │ Visualization │         │
      │ connectivity,  │    │               │         │
      │ errors)        │    │               │         │
      └───────┬────────┘    └───────────────┘         │
              │                                      │
      ┌───────▼────────┐                             │
      │ Keycloak       │                             │
      │ (AuthN / RBAC) │                             │
      └────────────────┘                             │
                                                     │
                                                      


## Core Components & Architectural Highlights

- Clients communicate through a **Load Balancer**, which distributes incoming requests across multiple FastAPI replicas (Uvicorn workers) to ensure high availability and efficient CPU utilization.  
- **Redis** serves as an in-memory cache for frequently accessed task data, reducing database load and improving response times for repeated queries.  
- **PostgreSQL** is the primary data store, with partitioned tables to optimize large datasets and read replicas to scale query performance for read-heavy operations.  
- **Celery**, in conjunction with a message broker (Redis or RabbitMQ), executes background tasks asynchronously, such as sending email notifications, without blocking API responses.  
- **Keycloak** handles secure authentication and role-based access control (RBAC), ensuring that API endpoints are accessed only by authorized users.  
- **Prometheus** monitors critical database health metrics, including connectivity status, query latency, and error rates, enabling proactive alerting and performance monitoring.
