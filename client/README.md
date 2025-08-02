# 🎨 Frontend - Smart Holiday Booking Assistant

A modern, responsive React frontend for the Smart Holiday Booking Assistant, built with Next.js 14, TypeScript, and Tailwind CSS. Features an intuitive chat interface with real-time trip planning capabilities.

## ✨ **Features**

### 🎯 **Core UI Components**
- **Chat-Style Interface**: Natural language trip planning input
- **Real-time Trip Generation**: Instant package recommendations
- **Responsive Design**: Mobile-first approach with adaptive layouts
- **Beautiful Animations**: Smooth transitions and hover effects

### 🚀 **Phase 1.5 Enhancements**
- **🔄 Regenerate Options**: One-click generation of new trip variations
- **🎯 Priority Toggles**: User-adjustable preferences for flight time, hotel quality, or cost
- **📱 Session Management**: Persistent session tracking across regenerations
- **🎨 Enhanced Visual Design**: Gradient backgrounds and glass morphism effects

### 🔐 **Authentication**
- **Firebase Integration**: Google Sign-In and Email/Password authentication
- **User Profile Display**: Avatar and name in header
- **Secure Token Management**: Automatic token handling for API requests
- **Session Persistence**: Maintains login state across page refreshes

### 📱 **User Experience**
- **Loading States**: Visual feedback during API calls
- **Error Handling**: Clear error messages and recovery options
- **Responsive Grid**: Adaptive card layout (1/2/3 columns)
- **Interactive Elements**: Hover effects and smooth animations

## 🎨 **Visual Design**

### **Color Scheme**
- **Primary Gradients**: Blue to purple gradients for main elements
- **Score Colors**: 
  - 🟢 Green (80+): Excellent options
  - 🟡 Amber (70-79): Good options  
  - 🔴 Red (<70): Fair options
- **Background**: Subtle gradient with glass morphism effects

### **Typography**
- **Headings**: Bold, modern sans-serif fonts
- **Body Text**: Clean, readable typography
- **Emojis**: Strategic use for visual appeal and clarity

### **Layout Components**
- **Header**: User authentication and branding
- **Main Container**: Glass morphism card with gradient background
- **Trip Cards**: Individual package displays with hover effects
- **Priority Panel**: Toggle controls for user preferences

## 🚀 **Quick Start**

### **Prerequisites**
- Node.js 18+ and npm
- Firebase project with Authentication enabled

### **Installation**
```bash
cd client
npm install
```

### **Environment Configuration**
```bash
cp .env.example .env.local
```

Add your Firebase configuration to `.env.local`:
```env
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your_measurement_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
```

### **Development**
```bash
npm run dev
```

Access the application at: http://localhost:3000

## 📁 **Project Structure**

```
client/
├── app/
│   ├── components/
│   │   └── AuthHeader.tsx          # Authentication UI component
│   ├── firebase.ts                 # Firebase configuration
│   ├── layout.tsx                  # Root layout with header
│   └── page.tsx                    # Main chat interface
├── public/                         # Static assets
├── .env.local                      # Environment variables
├── package.json                    # Dependencies and scripts
├── tailwind.config.js             # Tailwind CSS configuration
└── tsconfig.json                  # TypeScript configuration
```

## 🧩 **Component Details**

### **Main Page (`page.tsx`)**
The core application interface with the following features:

#### **State Management**
```typescript
const [input, setInput] = useState("");
const [loading, setLoading] = useState(false);
const [results, setResults] = useState<PlanTripResponse | null>(null);
const [error, setError] = useState("");
const [sessionId, setSessionId] = useState<string | null>(null);
const [priorities, setPriorities] = useState({
  prioritize_flight_time: false,
  prioritize_hotel_quality: false,
  prioritize_cost: false,
});
```

#### **Key Functions**
- `handleSubmit()`: Processes trip planning requests
- `handleRegenerate()`: Generates new trip variations
- `formatDate()`: Formats dates for display
- `formatCurrency()`: Formats currency values
- `getScoreColor()`: Returns color classes based on scores

### **Authentication Header (`AuthHeader.tsx`)**
Handles user authentication and profile display:

#### **Features**
- Google Sign-In integration
- User profile display (avatar + name)
- Sign-out functionality
- Responsive design

#### **Props**
```typescript
interface AuthHeaderProps {
  user: User | null;
  onSignIn: () => void;
  onSignOut: () => void;
}
```

### **Firebase Configuration (`firebase.ts`)**
Centralized Firebase setup and authentication management.

## 🎯 **Priority System**

### **Toggle Controls**
Three mutually exclusive priority settings:

1. **✈️ Prioritize Flight Time**
   - Optimizes for preferred flight times
   - Higher weight on flight scheduling
   - Better evening flight options

2. **🏨 Prioritize Hotel Quality**
   - Focuses on hotel location and amenities
   - Higher weight on proximity to POI
   - Better hotel selections

3. **💰 Prioritize Cost**
   - Emphasizes budget-friendly options
   - Higher weight on total cost
   - More economical packages

### **Implementation**
```typescript
const [priorities, setPriorities] = useState({
  prioritize_flight_time: false,
  prioritize_hotel_quality: false,
  prioritize_cost: false,
});

// Mutually exclusive toggles
onChange={(e) => setPriorities(prev => ({
  ...prev,
  prioritize_flight_time: e.target.checked,
  prioritize_hotel_quality: e.target.checked ? false : prev.prioritize_hotel_quality,
  prioritize_cost: e.target.checked ? false : prev.prioritize_cost,
}))}
```

## 🔄 **Regenerate Functionality**

### **Session Management**
- Each trip request gets a unique session ID
- Session persists across regenerations
- Tracks regeneration count in backend

### **Regenerate Button**
```typescript
const handleRegenerate = async () => {
  if (!sessionId) return;
  
  setLoading(true);
  setError("");
  
  try {
    const res = await fetch("http://localhost:8000/api/regenerate-trip", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: idToken ? `Bearer ${idToken}` : "",
      },
      body: JSON.stringify({ session_id: sessionId }),
    });
    
    const data = await res.json();
    setResults(data);
  } catch (err: any) {
    setError(err.message || "Failed to regenerate");
  } finally {
    setLoading(false);
  }
};
```

### **Visual Design**
- Cyclone emoji (🌀) for visual appeal
- Cyan-blue gradient button
- Loading spinner during regeneration
- Smooth transitions

## 🎨 **Styling Details**

### **Tailwind CSS Classes**
- **Gradients**: `bg-gradient-to-r from-blue-600 to-purple-600`
- **Glass Morphism**: `backdrop-blur-sm bg-white/10`
- **Hover Effects**: `hover:scale-105 transition-all duration-300`
- **Responsive Grid**: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`

### **Color Coding System**
```typescript
const getScoreColor = (score: number) => {
  if (score >= 80) {
    return "bg-gradient-to-r from-emerald-400 to-green-500"; // Excellent
  } else if (score >= 70) {
    return "bg-gradient-to-r from-amber-400 to-orange-500"; // Good
  } else {
    return "bg-gradient-to-r from-red-400 to-pink-500"; // Fair
  }
};
```

### **Responsive Design**
- **Mobile**: Single column layout
- **Tablet**: Two column grid
- **Desktop**: Three column grid
- **Touch-friendly**: Large touch targets

## 🔐 **Authentication Flow**

### **Firebase Integration**
1. **Configuration**: Firebase app initialization
2. **Sign-In**: Google authentication popup
3. **Token Management**: Automatic ID token handling
4. **API Requests**: Token included in Authorization header
5. **Session Persistence**: Login state maintained

### **Security Features**
- Secure token validation
- CORS protection
- Environment variable security
- Input sanitization

## 📊 **Data Display**

### **Trip Package Cards**
Each card displays:
- **Header**: Option number, dates, duration
- **Score Badge**: Color-coded score indicator
- **Total Cost**: Prominent pricing display
- **Flight Details**: Airline, times, cost
- **Hotel Details**: Name, location, nightly rate
- **Action Button**: "Book This Package" (placeholder)

### **Information Architecture**
- **Primary**: Score and total cost
- **Secondary**: Flight and hotel details
- **Tertiary**: Dates and duration
- **Actions**: Booking and regeneration options

## 🔌 **API Integration**

### **Endpoints Used**
- `POST /api/plan-trip`: Initial trip generation
- `POST /api/regenerate-trip`: Generate new variations
- `GET /api/trip-history/{user_id}`: User history (future)

### **Request Format**
```typescript
interface PlanTripRequest {
  destination: string;
  date_range: string[];
  num_travelers: number;
  preferences: {
    prefer_evening_flights: boolean;
    family_friendly_hotel: boolean;
    duration_range: number[];
    num_kids: number;
    prioritize_flight_time: boolean;
    prioritize_hotel_quality: boolean;
    prioritize_cost: boolean;
    other: Record<string, any>;
  };
}
```

### **Response Handling**
```typescript
interface PlanTripResponse {
  packages: TripPackage[];
  user_input: any;
  generated_at: string;
  session_id: string;
}
```

## 🧪 **Development Guidelines**

### **Code Style**
- **TypeScript**: Strict type checking enabled
- **ESLint**: Code quality and consistency
- **Prettier**: Automatic code formatting
- **Component Structure**: Functional components with hooks

### **Testing Strategy**
- **Unit Tests**: Component testing with Jest
- **Integration Tests**: API integration testing
- **E2E Tests**: User flow testing (planned)
- **Accessibility**: Screen reader compatibility

### **Performance Optimization**
- **Code Splitting**: Automatic Next.js optimization
- **Image Optimization**: Next.js Image component
- **Bundle Analysis**: Webpack bundle analyzer
- **Lazy Loading**: Component lazy loading

## 🚀 **Deployment**

### **Build Process**
```bash
npm run build
npm start
```

### **Environment Variables**
- Production Firebase configuration
- API endpoint URLs
- Analytics tracking IDs

### **Deployment Platforms**
- **Vercel**: Recommended for Next.js
- **Netlify**: Alternative deployment option
- **Firebase Hosting**: Google Cloud integration

## 🔮 **Future Enhancements**

### **Planned Features**
- **Trip History**: View past trip requests
- **Favorites**: Save preferred packages
- **Sharing**: Share trip plans with others
- **Notifications**: Real-time updates and alerts

### **UI Improvements**
- **Dark Mode**: Theme switching capability
- **Animations**: Enhanced micro-interactions
- **Accessibility**: WCAG compliance improvements
- **Internationalization**: Multi-language support

## 🆘 **Troubleshooting**

### **Common Issues**
1. **CORS Errors**: Check backend CORS configuration
2. **Authentication**: Verify Firebase configuration
3. **API Errors**: Check backend server status
4. **Styling Issues**: Clear browser cache

### **Debug Tools**
- **React DevTools**: Component inspection
- **Network Tab**: API request monitoring
- **Console Logs**: Error tracking
- **Performance Tab**: Load time analysis

---

**Built with ❤️ using Next.js, TypeScript, and Tailwind CSS**
