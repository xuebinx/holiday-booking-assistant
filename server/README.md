# 🚀 Backend - Smart Holiday Booking Assistant

A high-performance FastAPI backend for the Smart Holiday Booking Assistant, featuring intelligent trip optimization, session management, and comprehensive API endpoints. Built with Python, FastAPI, and MongoDB for scalable trip planning solutions.

## ✨ **Features**

### 🎯 **Core Backend Functionality**
- **AI-Powered Trip Optimization**: Intelligent scoring algorithm for travel packages
- **Real-time Package Generation**: Instant flight + hotel combinations
- **Multi-factor Scoring**: Cost, timing, location, and preference-based optimization
- **Session Management**: Complete trip planning session tracking

### 🚀 **Phase 1.5 Enhancements**
- **🔄 Regenerate Endpoint**: Generate new trip variations for existing sessions
- **🎯 Priority-Based Scoring**: Dynamic weight adjustment based on user preferences
- **📚 Session History**: Complete trip planning history with MongoDB
- **🔄 Session Persistence**: Unique session IDs and regeneration tracking

### 🔐 **Security & Authentication**
- **Firebase Integration**: Secure Firebase Admin SDK authentication
- **Token Validation**: Real-time Firebase ID token verification
- **CORS Protection**: Secure cross-origin request handling
- **Input Validation**: Comprehensive Pydantic model validation

### 📊 **Data Management**
- **MongoDB Integration**: Async MongoDB with Motor driver
- **Comprehensive Schemas**: Structured data models for all entities
- **Audit Trail**: Complete timestamp tracking and user association
- **Scalable Architecture**: Ready for production deployment

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Trip Optimizer │    │   MongoDB       │
│                 │    │                 │    │                 │
│ • API Endpoints │◄──►│ • Scoring Logic │◄──►│ • Trip Requests │
│ • Auth Middleware│    │ • Package Gen   │    │ • User History  │
│ • CORS Config   │    │ • Priority Mgmt │    │ • Sessions      │
│ • Validation    │    │ • Randomization │    │ • Analytics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+
- MongoDB (local or cloud)
- Firebase project with Admin SDK

### **Installation**
```bash
cd server
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### **Environment Configuration**
```bash
# Set environment variables
export MONGO_URI="mongodb://localhost:27017"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/firebase-credentials.json"
```

### **Development Server**
```bash
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Access Points**
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/

## 📁 **Project Structure**

```
server/
├── app/
│   ├── main.py                    # Main FastAPI application
│   └── trip_optimizer.py          # Trip optimization logic
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables
└── README.md                     # This file
```

## 🔌 **API Endpoints**

### **Core Endpoints**

#### **POST `/api/plan-trip`**
Generate optimized trip packages based on user preferences.

**Request Body:**
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
    "prioritize_flight_time": false,
    "prioritize_hotel_quality": false,
    "prioritize_cost": true,
    "other": { "poi": "National Gallery" }
  }
}
```

**Response:**
```json
{
  "packages": [
    {
      "flight": {
        "airline": "British Airways",
        "depart_time": "18:53",
        "arrive_time": "21:04",
        "cost": 101.0
      },
      "hotel": {
        "name": "Marriott London",
        "cost": 106.0,
        "distance_from_poi_km": 1.6
      },
      "total_score": 72.9,
      "total_cost": 1257.0,
      "duration": 3,
      "start_date": "2024-08-12",
      "end_date": "2024-08-15"
    }
  ],
  "user_input": {...},
  "generated_at": "2024-08-02T20:20:58.215193",
  "session_id": "744f43ab-8f5c-4f5f-b92f-167db8c00aa5"
}
```

#### **POST `/api/regenerate-trip`**
Generate new trip variations for an existing session.

**Request Body:**
```json
{
  "session_id": "744f43ab-8f5c-4f5f-b92f-167db8c00aa5"
}
```

**Response:** Same format as `/api/plan-trip`

#### **GET `/api/trip-history/{user_id}`**
Retrieve user's trip planning history.

**Parameters:**
- `user_id`: Firebase user ID
- `limit`: Number of sessions to return (default: 10)

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "744f43ab-8f5c-4f5f-b92f-167db8c00aa5",
      "destination": "London",
      "created_at": "2024-08-02T20:20:58.215193",
      "regeneration_count": 3,
      "generated_packages": [...]
    }
  ]
}
```

#### **GET `/`**
Health check endpoint.

**Response:**
```json
{
  "message": "Holiday Booking Assistant API is running."
}
```

## 🧠 **Trip Optimization Algorithm**

### **Enhanced Scoring System**

The system uses a dynamic weighted scoring algorithm that adapts based on user priorities:

#### **Default Weights**
| Factor | Weight | Description |
|--------|--------|-------------|
| **Cost** | 40% | Lower costs get higher scores |
| **Flight Time** | 30% | Preferred flight times |
| **Hotel Quality** | 25% | Proximity to POI and amenities |
| **Duration** | 5% | Longer stays preferred |

#### **Priority-Based Weight Adjustment**

**💰 Cost Priority (60% cost weight)**
- Cost: 60% (increased from 40%)
- Flight Time: 20% (decreased from 30%)
- Hotel Quality: 15% (decreased from 25%)
- Duration: 5% (unchanged)

**✈️ Flight Priority (50% flight weight)**
- Cost: 25% (decreased from 40%)
- Flight Time: 50% (increased from 30%)
- Hotel Quality: 20% (decreased from 25%)
- Duration: 5% (unchanged)

**🏨 Hotel Priority (50% hotel weight)**
- Cost: 25% (decreased from 40%)
- Flight Time: 20% (decreased from 30%)
- Hotel Quality: 50% (increased from 25%)
- Duration: 5% (unchanged)

### **Scoring Details**

#### **Cost Scoring (0-100 scale)**
```python
max_expected_cost = 2000  # £2000 baseline
cost_score = max(0, 100 - (total_cost / max_expected_cost) * 100)
```

#### **Flight Time Scoring**
- **Evening Flights (18:00-22:00)**: 100 points
- **Morning Flights (06:00-12:00)**: 50 points
- **Afternoon Flights (12:00-18:00)**: 30 points
- **Night Flights (22:00-06:00)**: 20 points

#### **Hotel Quality Scoring**
- **≤ 1.0 km from POI**: 100 points
- **≤ 2.0 km from POI**: 80 points
- **≤ 3.0 km from POI**: 60 points
- **> 3.0 km from POI**: 40 points
- **Family-friendly bonus**: +20 points

#### **Duration Scoring**
- **5+ days**: 100 points
- **4 days**: 80 points
- **3 days**: 60 points
- **< 3 days**: 40 points

## 📊 **Data Models**

### **Request Models**

#### **TripPreferences**
```python
class TripPreferences(BaseModel):
    prefer_evening_flights: bool = False
    family_friendly_hotel: bool = False
    duration_range: List[int] = Field(default=[3, 5])
    num_kids: int = Field(default=0)
    prioritize_flight_time: bool = Field(default=False)
    prioritize_hotel_quality: bool = Field(default=False)
    prioritize_cost: bool = Field(default=False)
    other: Dict[str, Any] = Field(default_factory=dict)
```

#### **PlanTripRequest**
```python
class PlanTripRequest(BaseModel):
    destination: str
    date_range: List[date]
    num_travelers: int
    preferences: TripPreferences
```

### **Response Models**

#### **TripPackage**
```python
class TripPackage(BaseModel):
    flight: FlightDetails
    hotel: HotelDetails
    total_score: float
    total_cost: float
    duration: int
    start_date: date
    end_date: date
```

#### **PlanTripResponse**
```python
class PlanTripResponse(BaseModel):
    packages: List[TripPackage]
    user_input: dict
    generated_at: datetime
    session_id: str
```

### **Database Models**

#### **TripRequestDB**
```python
class TripRequestDB(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    destination: str
    date_range: List[date]
    num_travelers: int
    preferences: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    generated_packages: List[Dict[str, Any]] = Field(default_factory=list)
    generated_at: Optional[datetime] = None
    regeneration_count: int = Field(default=0)
```

## 🔐 **Authentication Setup**

### **Firebase Admin SDK Configuration**

1. **Download Service Account Key**
   - Go to Firebase Console → Project Settings → Service Accounts
   - Generate new private key
   - Save as JSON file

2. **Set Environment Variable**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
   ```

3. **Enable Authentication**
   ```python
   import firebase_admin
   from firebase_admin import credentials, auth
   
   cred = credentials.Certificate("path/to/service-account-key.json")
   firebase_admin.initialize_app(cred)
   ```

### **Token Validation**
```python
def verify_firebase_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    id_token = auth_header.split("Bearer ")[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## 🗄️ **Database Integration**

### **MongoDB Setup**

#### **Connection Configuration**
```python
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = mongo_client["holiday_booking"]
trip_requests_collection = db["trip_requests"]
```

#### **Data Operations**
```python
# Insert new trip request
await trip_requests_collection.insert_one(trip_db_to_mongo(trip_db))

# Find existing session
session = await trip_requests_collection.find_one({"session_id": session_id})

# Update regeneration count
await trip_requests_collection.update_one(
    {"session_id": session_id},
    {"$inc": {"regeneration_count": 1}}
)
```

### **Data Serialization**
```python
def trip_db_to_mongo(trip_db: TripRequestDB):
    doc = trip_db.dict()
    doc["date_range"] = [d.isoformat() for d in doc["date_range"]]
    if isinstance(doc["created_at"], datetime):
        doc["created_at"] = doc["created_at"].isoformat()
    if isinstance(doc["generated_at"], datetime):
        doc["generated_at"] = doc["generated_at"].isoformat()
    return doc
```

## 🧪 **Development Guidelines**

### **Code Structure**
- **FastAPI**: Modern async web framework
- **Pydantic**: Data validation and serialization
- **Motor**: Async MongoDB driver
- **Type Hints**: Full type annotation support

### **Error Handling**
```python
from fastapi import HTTPException

# Custom error responses
if not session:
    raise HTTPException(status_code=404, detail="Session not found")

# Validation errors
except ValidationError as e:
    raise HTTPException(status_code=422, detail=str(e))
```

### **Testing Strategy**
- **Unit Tests**: Individual function testing
- **Integration Tests**: API endpoint testing
- **Database Tests**: MongoDB integration testing
- **Authentication Tests**: Firebase token validation

### **Performance Optimization**
- **Async Operations**: Non-blocking database operations
- **Connection Pooling**: Efficient MongoDB connections
- **Caching**: Redis integration (planned)
- **Load Balancing**: Horizontal scaling ready

## 🚀 **Deployment**

### **Production Setup**
```bash
# Install production dependencies
pip install -r requirements.txt

# Set production environment variables
export MONGO_URI="mongodb+srv://..."
export GOOGLE_APPLICATION_CREDENTIALS="..."

# Start production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### **Docker Deployment**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Environment Variables**
```bash
# Required
MONGO_URI=mongodb://localhost:27017
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# Optional
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:3002
```

## 📊 **Monitoring & Logging**

### **Performance Metrics**
- **Response Times**: API endpoint performance tracking
- **Database Queries**: MongoDB operation monitoring
- **Error Rates**: Exception tracking and alerting
- **User Activity**: Trip generation and regeneration metrics

### **Logging Configuration**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
```

### **Health Checks**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

## 🔮 **Future Enhancements**

### **Phase 2 Features**
- **Real API Integration**: Live flight and hotel data
- **Payment Processing**: Secure payment gateway integration
- **Booking Confirmation**: Email notifications and confirmations
- **Advanced Analytics**: User behavior and preference analysis

### **Technical Improvements**
- **Redis Caching**: Performance optimization
- **Rate Limiting**: API usage control
- **GraphQL**: Flexible query interface
- **Microservices**: Service decomposition

### **Advanced Features**
- **Multi-destination Trips**: Complex itinerary planning
- **Group Optimization**: Group booking algorithms
- **Seasonal Pricing**: Dynamic pricing analysis
- **AI Recommendations**: Machine learning integration

## 🆘 **Troubleshooting**

### **Common Issues**

#### **MongoDB Connection**
```bash
# Check MongoDB status
sudo systemctl status mongod

# Test connection
python3 -c "import motor; print('MongoDB OK')"
```

#### **Firebase Authentication**
```bash
# Verify credentials
python3 -c "import firebase_admin; print('Firebase OK')"

# Check environment variable
echo $GOOGLE_APPLICATION_CREDENTIALS
```

#### **CORS Issues**
```python
# Update CORS origins
origins = [
    "http://localhost:3000",
    "http://localhost:3002",
    "https://yourdomain.com"
]
```

### **Debug Mode**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python3 -m uvicorn app.main:app --reload --log-level debug
```

### **Performance Analysis**
```bash
# Install profiling tools
pip install py-spy

# Profile application
py-spy top -- python3 -m uvicorn app.main:app
```

---

**Built with ❤️ using FastAPI, Python, and MongoDB** 