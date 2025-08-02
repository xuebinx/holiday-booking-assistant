# 🏖️ Smart Holiday Booking Assistant

A full-stack AI-powered holiday booking assistant that helps users plan their perfect trips through an intuitive chat interface. The system generates optimized travel packages based on user preferences and provides intelligent recommendations.

## ✨ **Features**

### 🎯 **Core Functionality**
- **AI-Powered Trip Planning**: Natural language processing for trip intent
- **Smart Package Generation**: Optimized flight + hotel combinations
- **Intelligent Scoring**: Multi-factor scoring algorithm (cost, timing, location, preferences)
- **Real-time Recommendations**: Instant trip package suggestions

### 🚀 **Phase 1.5 Enhancements**
- **🔄 Regenerate Options**: Generate new trip variations with the "🌀 Regenerate Options" button
- **🎯 User-Adjustable Priorities**: Toggle between prioritizing flight time, hotel quality, or cost
- **📚 Session History**: Complete trip planning history stored in MongoDB
- **🔄 Session Management**: Unique session IDs for tracking and regeneration

### 🔐 **Authentication & Security**
- **Firebase Authentication**: Google Sign-In and Email/Password
- **Secure API**: Firebase ID token validation
- **CORS Protection**: Cross-origin request security

### 📱 **User Experience**
- **Responsive Design**: Mobile-friendly interface
- **Real-time Feedback**: Loading states and error handling
- **Beautiful UI**: Modern gradient design with glass morphism effects
- **Interactive Elements**: Hover effects and smooth animations

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (MongoDB)     │
│                 │    │                 │    │                 │
│ • React UI      │    │ • Trip Planning │    │ • Trip Requests │
│ • Firebase Auth │    │ • Optimization  │    │ • User History  │
│ • Real-time     │    │ • Session Mgmt  │    │ • Analytics     │
│   Updates       │    │ • API Endpoints │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 **Quick Start**

### **Prerequisites**
- Node.js 18+ and npm
- Python 3.8+
- MongoDB (local or cloud)
- Firebase project (for authentication)

### **1. Clone and Setup**
```bash
git clone <repository-url>
cd holiday-booking-assistant
```

### **2. Backend Setup**
```bash
cd server
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export MONGO_URI="mongodb://localhost:27017"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/firebase-credentials.json"

# Start the server
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **3. Frontend Setup**
```bash
cd client
npm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local with your Firebase config

# Start the development server
npm run dev
```

### **4. Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📁 **Project Structure**

```
holiday-booking-assistant/
├── client/                          # Next.js Frontend
│   ├── app/
│   │   ├── components/
│   │   │   └── AuthHeader.tsx      # Authentication UI
│   │   ├── firebase.ts             # Firebase configuration
│   │   ├── layout.tsx              # Root layout
│   │   └── page.tsx                # Main chat interface
│   ├── public/
│   └── package.json
├── server/                          # FastAPI Backend
│   ├── app/
│   │   ├── main.py                 # Main API endpoints
│   │   └── trip_optimizer.py       # Trip optimization logic
│   ├── requirements.txt
│   └── README.md
└── README.md                        # This file
```

## 🔌 **API Endpoints**

### **Core Endpoints**
- `POST /api/plan-trip` - Generate trip packages
- `POST /api/regenerate-trip` - Generate new variations for existing session
- `GET /api/trip-history/{user_id}` - Retrieve user's trip history

### **Request Format**
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

### **Response Format**
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

## 🧠 **Trip Optimization Algorithm**

### **Scoring Criteria**
The system uses a weighted scoring algorithm that considers:

| Factor | Weight (Default) | Weight (Cost Priority) | Weight (Flight Priority) | Weight (Hotel Priority) |
|--------|------------------|------------------------|--------------------------|-------------------------|
| **Cost** | 40% | 60% | 25% | 25% |
| **Flight Time** | 30% | 20% | 50% | 20% |
| **Hotel Quality** | 25% | 15% | 20% | 50% |
| **Duration** | 5% | 5% | 5% | 5% |

### **Priority System**
- **💰 Cost Priority**: Emphasizes budget-friendly options
- **✈️ Flight Priority**: Optimizes for preferred flight times
- **🏨 Hotel Priority**: Focuses on hotel quality and location

### **Scoring Details**
- **Cost Score**: Lower costs get higher scores (0-100 scale)
- **Flight Score**: Evening flights preferred if specified (100/50/30 points)
- **Hotel Score**: Closer to POI gets higher scores (100/80/60/40 points)
- **Duration Score**: Longer stays preferred (100/80/60/40 points)

## 🎨 **UI Components**

### **Main Interface**
- **Chat Input**: Natural language trip description
- **Priority Toggles**: Three mutually exclusive priority settings
- **Trip Cards**: Beautiful cards showing flight, hotel, and pricing details
- **Regenerate Button**: Generate new variations with cyclone emoji

### **Visual Design**
- **Gradient Backgrounds**: Modern blue-purple gradients
- **Glass Morphism**: Translucent card effects
- **Color-Coded Scores**: Green (excellent), Amber (good), Red (fair)
- **Responsive Grid**: Mobile-friendly card layout

## 🔐 **Security Features**

### **Authentication**
- Firebase Authentication integration
- Google Sign-In support
- Email/Password authentication
- Secure token validation

### **API Security**
- CORS protection for cross-origin requests
- Firebase ID token validation
- Input sanitization and validation
- Rate limiting (planned)

## 🗄️ **Data Management**

### **MongoDB Collections**
- `trip_requests`: Complete trip planning sessions
- Session tracking with regeneration counts
- User association for history
- Timestamp tracking for analytics

### **Session Management**
- Unique session IDs for each trip request
- Regeneration tracking and history
- User preference persistence
- Complete audit trail

## 🧪 **Development & Testing**

### **Development Scripts**
```bash
# Backend
cd server
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd client
npm run dev
```

### **Testing**
- API testing with FastAPI's automatic docs
- Frontend testing with Next.js development tools
- MongoDB integration testing
- CORS and authentication testing

## 🚀 **Deployment**

### **Backend Deployment**
- FastAPI with Uvicorn ASGI server
- MongoDB Atlas for cloud database
- Firebase Admin SDK for authentication
- Environment variable configuration

### **Frontend Deployment**
- Next.js static export or Vercel deployment
- Firebase hosting integration
- Environment variable management
- CDN optimization

## 📊 **Monitoring & Analytics**

### **Performance Metrics**
- API response times
- Trip generation success rates
- User engagement metrics
- Regeneration frequency

### **Error Tracking**
- Comprehensive error logging
- User feedback collection
- Performance monitoring
- Debug information capture

## 🔮 **Future Enhancements**

### **Phase 2 Features**
- Real flight/hotel API integration
- Payment processing
- Booking confirmation
- Email notifications

### **Advanced Features**
- Multi-destination trips
- Group booking optimization
- Seasonal pricing analysis
- AI-powered recommendations

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 **Support**

For support and questions:
- Check the API documentation at `/docs`
- Review the troubleshooting guides
- Open an issue on GitHub

---

**Built with ❤️ using Next.js, FastAPI, and MongoDB** 