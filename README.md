# 🏖️ Smart Holiday Booking Assistant

A full-stack AI-powered holiday booking assistant that helps users find optimized travel packages through an intuitive chat interface. The system uses intelligent scoring algorithms to recommend the best flight and hotel combinations based on user preferences.

## ✨ Features

### 🤖 Smart Trip Optimization
- **Intelligent Scoring Algorithm**: Multi-criteria optimization with 40% cost weight, flight time preferences, hotel proximity, and family-friendliness
- **Flexible Date Ranges**: Generates 3-5 day travel windows within user's specified date range
- **Preference Matching**: Evening flights, family-friendly hotels, proximity to points of interest
- **Real-time Recommendations**: Returns top 3 optimized trip packages

### 🎨 Modern User Interface
- **Chat-Style Interface**: Intuitive conversation flow for trip planning
- **Responsive Design**: Mobile-friendly grid layout (1/2/3 columns for mobile/tablet/desktop)
- **Beautiful Cards**: Clean display of flight details, hotel information, costs, and scores
- **Real-time Feedback**: Loading states, error handling, and success messages

### 🔐 Secure Authentication
- **Firebase Authentication**: Google sign-in integration
- **Token Validation**: Secure backend validation of Firebase ID tokens
- **User Session Management**: Persistent login state with user profile display

### 📊 Rich Data Management
- **MongoDB Integration**: Stores trip requests and generated packages
- **Comprehensive Data**: Flight details, hotel information, pricing, scoring
- **Historical Tracking**: Timestamped requests and recommendations

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (MongoDB)     │
│   Port: 3002    │    │   Port: 8000    │    │   Port: 27017   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│  Firebase Auth  │    │ Trip Optimizer  │
│  (Google Sign-in)│    │  (Python Module)│
└─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- MongoDB (local or cloud)
- Firebase project with Authentication enabled

### 1. Clone and Setup
```bash
git clone <repository-url>
cd holiday-booking-assistant
```

### 2. Backend Setup
```bash
cd server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MONGO_URI="mongodb://localhost:27017"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/firebase-service-account.json"

# Start server
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
cd client

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Add your Firebase config to .env.local:
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your_measurement_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id

# Start development server
npm run dev
```

### 4. Access the Application
- **Frontend**: http://localhost:3002 (or available port)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
holiday-booking-assistant/
├── client/                          # Next.js Frontend
│   ├── app/
│   │   ├── components/
│   │   │   └── AuthHeader.tsx      # Firebase auth component
│   │   ├── firebase.ts             # Firebase configuration
│   │   ├── layout.tsx              # Root layout with header
│   │   └── page.tsx                # Main chat interface
│   ├── .env.local                  # Environment variables
│   ├── package.json
│   └── tailwind.config.js
├── server/                          # FastAPI Backend
│   ├── app/
│   │   ├── main.py                 # Main API endpoints
│   │   └── trip_optimizer.py       # Trip optimization logic
│   ├── requirements.txt
│   └── .env                        # Backend environment
└── README.md
```

## 🔧 API Endpoints

### POST `/api/plan-trip`
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
    "other": {
      "poi": "National Gallery"
    }
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
  "user_input": {...},
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### GET `/`
Health check endpoint.

## 🧠 Trip Optimization Algorithm

The system uses a sophisticated scoring algorithm that considers:

### Scoring Criteria (Total: 100 points)
- **Cost (40%)**: Lower costs receive higher scores
- **Flight Time (30%)**: Evening flights preferred if specified
- **Hotel Proximity (25%)**: Closer to POI gets higher scores
- **Family-Friendly (15%)**: Bonus for family-friendly hotels
- **Duration Bonus**: Longer stays (5+ days) get additional points

### Optimization Process
1. **Generate Travel Windows**: Creates all valid 3-5 day combinations within date range
2. **Flight Options**: 3 flight options per window with varying times and costs
3. **Hotel Options**: 3 hotel options with different locations and amenities
4. **Package Creation**: Combines flights and hotels into complete packages
5. **Scoring**: Applies preference-based scoring algorithm
6. **Ranking**: Returns top 3 highest-scoring packages

## 🎨 UI Components

### Chat Interface
- **Input Field**: Text input for trip requests
- **Send Button**: Submit requests to backend
- **Loading Spinner**: Visual feedback during processing
- **Error Messages**: Clear error display

### Trip Package Cards
- **Header**: Option number, date range, duration
- **Score Badge**: Visual score indicator
- **Total Cost**: Prominent cost display
- **Flight Section**: Airline, times, cost
- **Hotel Section**: Name, location, nightly rate
- **Responsive Grid**: Adapts to screen size

### Authentication Header
- **User Avatar**: Google profile picture
- **User Name**: Display name or email
- **Sign Out**: Logout functionality
- **Sign In**: Google authentication button

## 🔐 Security Features

- **Firebase Authentication**: Secure Google sign-in
- **Token Validation**: Backend verification of Firebase ID tokens
- **CORS Configuration**: Secure cross-origin requests
- **Environment Variables**: Secure configuration management

## 🛠️ Development

### Adding New Features
1. **Backend**: Add endpoints in `server/app/main.py`
2. **Frontend**: Create components in `client/app/components/`
3. **Optimization**: Extend `server/app/trip_optimizer.py`

### Testing
```bash
# Backend tests
cd server
python -m pytest

# Frontend tests
cd client
npm test
```

### Deployment
- **Frontend**: Deploy to Vercel/Netlify
- **Backend**: Deploy to Railway/Render/AWS
- **Database**: Use MongoDB Atlas for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the Firebase console for authentication issues

---

**Built with ❤️ using Next.js, FastAPI, MongoDB, and Firebase** 