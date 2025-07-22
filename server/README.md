# 🚀 Holiday Booking Assistant - Backend

A high-performance FastAPI backend for the Smart Holiday Booking Assistant featuring intelligent trip optimization, MongoDB integration, and Firebase authentication.

## ✨ Features

### 🤖 Smart Trip Optimization
- **Intelligent Scoring Algorithm**: Multi-criteria optimization with configurable weights
- **Flexible Date Ranges**: Generates 3-5 day travel windows within user's date range
- **Preference Matching**: Evening flights, family-friendly hotels, POI proximity
- **Real-time Recommendations**: Returns top 3 optimized trip packages

### 🔐 Authentication & Security
- **Firebase Admin SDK**: Secure backend validation of Firebase ID tokens
- **CORS Configuration**: Secure cross-origin requests for frontend
- **Environment Variables**: Secure configuration management
- **Token Validation**: Automatic verification of authentication headers

### 📊 Data Management
- **MongoDB Integration**: Async database operations with Motor
- **Comprehensive Schemas**: Pydantic models for request/response validation
- **Historical Tracking**: Timestamped requests and generated packages
- **Data Persistence**: Stores both user input and optimization results

### 🚀 Performance
- **Async Operations**: Non-blocking database and API operations
- **FastAPI Framework**: High-performance Python web framework
- **Uvicorn Server**: ASGI server with hot reload for development
- **Optimized Queries**: Efficient MongoDB operations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB (local or cloud)
- Firebase project with Admin SDK credentials

### Installation
```bash
cd server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration
Create a `.env` file or set environment variables:

```env
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017

# Firebase Admin SDK
GOOGLE_APPLICATION_CREDENTIALS=path/to/firebase-service-account.json

# Optional: Custom port
PORT=8000
```

### Development
```bash
# Start development server with hot reload
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start production server
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run tests
python -m pytest

# Run linting
flake8 app/
```

### Access the API
- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

## 📁 Project Structure

```
server/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application and endpoints
│   └── trip_optimizer.py          # Trip optimization algorithm
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables
├── .gitignore
└── README.md
```

## 🔧 API Endpoints

### POST `/api/plan-trip`
Generate optimized trip packages based on user preferences.

**Authentication**: Requires Firebase ID token in Authorization header

**Request Body**:
```json
{
  "destination": "London",
  "date_range": ["2024-08-10", "2024-08-15"],
  "num_travelers": 3,
  "preferences": {
    "prefer_evening_flights": true,
    "family_friendly_hotel": true,
    "duration_range": [3, 5],
    "num_kids": 2,
    "other": {
      "poi": "National Gallery"
    }
  }
}
```

**Response**:
```json
{
  "packages": [
    {
      "flight": {
        "airline": "British Airways",
        "depart_time": "19:30",
        "arrive_time": "21:45",
        "cost": 180.0
      },
      "hotel": {
        "name": "Hilton London",
        "cost": 120.0,
        "distance_from_poi_km": 1.2
      },
      "total_score": 85.5,
      "total_cost": 1080.0,
      "duration": 4,
      "start_date": "2024-08-10",
      "end_date": "2024-08-14"
    }
  ],
  "user_input": {
    "destination": "London",
    "date_range": ["2024-08-10", "2024-08-15"],
    "num_travelers": 3,
    "preferences": {...}
  },
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### GET `/`
Health check endpoint.

**Response**:
```json
{
  "message": "Holiday Booking Assistant API is running."
}
```

## 🧠 Trip Optimization Algorithm

### Scoring Criteria (Total: 100 points)

| Criteria | Weight | Description |
|----------|--------|-------------|
| **Cost** | 40% | Lower costs receive higher scores |
| **Flight Time** | 30% | Evening flights preferred if specified |
| **Hotel Proximity** | 25% | Closer to POI gets higher scores |
| **Family-Friendly** | 15% | Bonus for family-friendly hotels |
| **Duration Bonus** | +10 | Longer stays (5+ days) get additional points |

### Optimization Process

1. **Generate Travel Windows**
   ```python
   # Creates all valid 3-5 day combinations within date range
   travel_windows = generate_travel_windows(start_date, end_date, duration_range)
   ```

2. **Flight Options Generation**
   ```python
   # 3 flight options per window with varying times and costs
   flight_options = generate_flight_options(destination, window, preferences)
   ```

3. **Hotel Options Generation**
   ```python
   # 3 hotel options with different locations and amenities
   hotel_options = generate_hotel_options(destination, window, preferences)
   ```

4. **Package Creation**
   ```python
   # Combines flights and hotels into complete packages
   packages = create_trip_packages(flights, hotels, window, num_travelers)
   ```

5. **Scoring & Ranking**
   ```python
   # Applies preference-based scoring algorithm
   scored_packages = score_and_rank_packages(packages, preferences)
   ```

## 📊 Data Models

### Request Models
```python
class TripPreferences(BaseModel):
    prefer_evening_flights: bool = False
    family_friendly_hotel: bool = False
    duration_range: List[int] = Field(default=[3, 5])
    num_kids: int = Field(default=0)
    other: Dict[str, Any] = Field(default_factory=dict)

class PlanTripRequest(BaseModel):
    destination: str
    date_range: List[date]
    num_travelers: int
    preferences: TripPreferences
```

### Response Models
```python
class FlightDetails(BaseModel):
    airline: str
    depart_time: str
    arrive_time: str
    cost: float

class HotelDetails(BaseModel):
    name: str
    cost: float
    distance_from_poi_km: float

class TripPackage(BaseModel):
    flight: FlightDetails
    hotel: HotelDetails
    total_score: float
    total_cost: float
    duration: int
    start_date: date
    end_date: date
```

### Database Models
```python
class TripRequestDB(BaseModel):
    destination: str
    date_range: List[date]
    num_travelers: int
    preferences: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    generated_packages: List[Dict[str, Any]] = Field(default_factory=list)
    generated_at: Optional[datetime] = None
```

## 🔐 Authentication

### Firebase Admin SDK Setup
```python
# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        firebase_admin.initialize_app()
```

### Token Validation
```python
def verify_firebase_token(request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    id_token = auth_header.split(" ", 1)[1]
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        return decoded_token
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Firebase ID token")
```

## 🗄️ Database Integration

### MongoDB Setup
```python
# Async MongoDB client with Motor
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = mongo_client["holiday_booking"]
trip_requests_collection = db["trip_requests"]
```

### Database Operations
```python
# Store trip request and results
async def store_trip_request(trip_data: dict):
    result = await trip_requests_collection.insert_one(trip_data)
    return result.inserted_id

# Query historical requests
async def get_trip_history(user_id: str, limit: int = 10):
    cursor = trip_requests_collection.find(
        {"user_id": user_id}
    ).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)
```

## 🛠️ Development

### Adding New Endpoints
1. Define Pydantic models for request/response
2. Create endpoint function with proper decorators
3. Add authentication if required
4. Implement business logic
5. Add error handling

### Example Endpoint
```python
@app.get("/api/trip-history/{user_id}")
async def get_user_trip_history(user_id: str, limit: int = 10):
    # Verify authentication
    verify_firebase_token(request)
    
    # Query database
    history = await get_trip_history(user_id, limit)
    
    return {"trips": history}
```

### Error Handling
```python
from fastapi import HTTPException, status

# Custom exceptions
class TripOptimizationError(Exception):
    pass

# Error handling in endpoints
try:
    result = await optimize_trip(request_data)
except TripOptimizationError as e:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(e)
    )
```

### Testing
```python
# Test endpoint
def test_plan_trip():
    client = TestClient(app)
    response = client.post("/api/plan-trip", json=test_data)
    assert response.status_code == 200
    assert "packages" in response.json()

# Test optimization algorithm
def test_trip_optimizer():
    result = generate_trip_options(test_intent)
    assert len(result) <= 3
    assert all("total_score" in pkg for pkg in result)
```

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Railway/Render Deployment
1. Connect GitHub repository
2. Set environment variables:
   - `MONGO_URI`
   - `GOOGLE_APPLICATION_CREDENTIALS`
3. Deploy automatically

### AWS/Google Cloud Deployment
```bash
# Build and deploy
gcloud app deploy app.yaml

# Or with Docker
docker build -t holiday-booking-api .
docker run -p 8000:8000 holiday-booking-api
```

### Environment Variables for Production
```env
# Database
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/holiday_booking

# Firebase
GOOGLE_APPLICATION_CREDENTIALS=base64_encoded_service_account_json

# Security
CORS_ORIGINS=https://your-frontend-domain.com

# Performance
WORKERS=4
MAX_CONNECTIONS=1000
```

## 📈 Monitoring & Logging

### Logging Configuration
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log API requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response
```

### Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

## 🐛 Troubleshooting

### Common Issues
1. **MongoDB Connection**: Check MONGO_URI and network connectivity
2. **Firebase Auth**: Verify service account credentials
3. **CORS Errors**: Ensure frontend URL is in CORS origins
4. **Import Errors**: Check Python path and virtual environment

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python3 -m uvicorn app.main:app --reload --log-level debug
```

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Motor (Async MongoDB)](https://motor.readthedocs.io/)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin)
- [Pydantic Models](https://pydantic-docs.helpmanual.io/)
- [Uvicorn Server](https://www.uvicorn.org/)

---

**Built with ❤️ using FastAPI, MongoDB, and Firebase Admin SDK** 