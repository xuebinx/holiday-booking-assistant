# 🎨 Holiday Booking Assistant - Frontend

A modern, responsive React frontend for the Smart Holiday Booking Assistant built with Next.js 15, Tailwind CSS, and Firebase Authentication.

## ✨ Features

### 🎯 User Interface
- **Chat-Style Interface**: Intuitive conversation flow for trip planning
- **Responsive Design**: Mobile-first approach with adaptive layouts
- **Beautiful Cards**: Clean display of trip packages with flight and hotel details
- **Real-time Feedback**: Loading states, error handling, and success messages

### 🔐 Authentication
- **Firebase Authentication**: Google sign-in integration
- **User Session Management**: Persistent login state
- **Profile Display**: User avatar and name in header
- **Secure Token Handling**: Automatic token inclusion in API requests

### 📱 Responsive Layout
- **Mobile**: Single column layout for optimal mobile experience
- **Tablet**: Two-column grid for medium screens
- **Desktop**: Three-column grid for large screens
- **Touch Optimized**: Mobile-friendly interactions

### 🎨 Visual Design
- **Modern UI**: Clean, professional design with Tailwind CSS
- **Color Coding**: Blue for flights, green for costs, orange for scores
- **Icons**: ✈️ for flights, 🏨 for hotels
- **Typography**: Clear hierarchy and readable fonts

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Firebase project with Authentication enabled

### Installation
```bash
cd client

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local
```

### Environment Configuration
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

### Development
```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run tests
npm test

# Run linting
npm run lint
```

### Access the Application
- **Development**: http://localhost:3002 (or available port)
- **Network**: http://192.168.0.166:3002 (for mobile testing)

## 📁 Project Structure

```
client/
├── app/                              # Next.js App Router
│   ├── components/
│   │   └── AuthHeader.tsx           # Firebase authentication component
│   ├── firebase.ts                  # Firebase configuration
│   ├── globals.css                  # Global styles
│   ├── layout.tsx                   # Root layout with header
│   └── page.tsx                     # Main chat interface
├── public/                          # Static assets
├── .env.local                       # Environment variables
├── .gitignore
├── next.config.js                   # Next.js configuration
├── package.json                     # Dependencies and scripts
├── tailwind.config.js              # Tailwind CSS configuration
└── tsconfig.json                   # TypeScript configuration
```

## 🧩 Components

### AuthHeader.tsx
Firebase authentication component that handles:
- **Google Sign-in**: OAuth authentication flow
- **User Display**: Shows user avatar and name
- **Sign Out**: Logout functionality
- **Loading States**: Handles authentication state changes

```tsx
// Usage in layout.tsx
<AuthHeader />
```

### Main Chat Interface (page.tsx)
The primary user interface featuring:
- **Input Field**: Text input for trip requests
- **Send Button**: Submit requests to backend API
- **Loading Spinner**: Visual feedback during processing
- **Trip Cards**: Display optimized travel packages
- **Error Handling**: Clear error messages

### Firebase Configuration (firebase.ts)
Centralized Firebase setup:
- **App Initialization**: Single Firebase app instance
- **Auth Export**: Authentication service export
- **Environment Variables**: Secure configuration management

## 🎨 Styling

### Tailwind CSS
The project uses Tailwind CSS for styling with custom configuration:

```javascript
// tailwind.config.js
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Custom color palette
      }
    },
  },
  plugins: [],
}
```

### Responsive Design
- **Mobile First**: Base styles for mobile devices
- **Breakpoints**: 
  - `sm`: 640px+ (small tablets)
  - `md`: 768px+ (tablets)
  - `lg`: 1024px+ (desktops)
  - `xl`: 1280px+ (large desktops)

### Component Styling
```tsx
// Example responsive grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Trip package cards */}
</div>
```

## 🔐 Authentication Flow

### 1. User Sign-in
```tsx
const handleGoogleSignIn = async () => {
  const provider = new GoogleAuthProvider();
  await signInWithPopup(auth, provider);
};
```

### 2. Token Management
```tsx
// Get Firebase ID token for API requests
const user = auth.currentUser;
if (user) {
  const idToken = await user.getIdToken();
  // Include in Authorization header
}
```

### 3. API Integration
```tsx
const response = await fetch('/api/plan-trip', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${idToken}`,
  },
  body: JSON.stringify(requestData),
});
```

## 📊 Data Display

### Trip Package Cards
Each card displays:
- **Header**: Option number, date range, duration
- **Score Badge**: Visual score indicator with color coding
- **Total Cost**: Prominent cost display in GBP
- **Flight Section**: Airline, departure/arrival times, cost
- **Hotel Section**: Name, location, nightly rate, POI distance

### Data Formatting
```tsx
// Currency formatting
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-GB', {
    style: 'currency',
    currency: 'GBP'
  }).format(amount);
};

// Date formatting
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: 'numeric'
  });
};
```

## 🔧 API Integration

### Backend Communication
- **Base URL**: http://localhost:8000 (development)
- **CORS**: Configured for cross-origin requests
- **Authentication**: Firebase ID token in Authorization header
- **Error Handling**: HTTP status code handling

### Request Format
```tsx
const requestData = {
  destination: userInput,
  date_range: ["2024-08-10", "2024-08-15"],
  num_travelers: 3,
  preferences: {
    prefer_evening_flights: true,
    family_friendly_hotel: true,
    duration_range: [3, 5],
    num_kids: 2,
    other: { poi: "National Gallery" },
  },
};
```

## 🛠️ Development

### Adding New Components
1. Create component in `app/components/`
2. Export from component file
3. Import and use in pages

### State Management
- **useState**: Local component state
- **useEffect**: Side effects and API calls
- **Context**: Firebase auth state (if needed)

### TypeScript
The project uses TypeScript for type safety:
```tsx
interface TripPackage {
  flight: FlightDetails;
  hotel: HotelDetails;
  total_score: number;
  total_cost: number;
  duration: number;
  start_date: string;
  end_date: string;
}
```

### Testing
```bash
# Run tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

## 🚀 Deployment

### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard
```

### Netlify
```bash
# Build the project
npm run build

# Deploy to Netlify
# Upload the .next folder or connect GitHub repository
```

### Environment Variables
Ensure all Firebase environment variables are set in your deployment platform:
- `NEXT_PUBLIC_FIREBASE_API_KEY`
- `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
- `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
- `NEXT_PUBLIC_FIREBASE_APP_ID`
- `NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID`
- `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET`
- `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`

## 🐛 Troubleshooting

### Common Issues
1. **Port Already in Use**: Next.js will automatically use the next available port
2. **Firebase Auth Errors**: Check environment variables and Firebase console settings
3. **CORS Errors**: Ensure backend CORS is configured for your frontend URL
4. **Build Errors**: Check TypeScript types and import statements

### Debug Mode
```bash
# Enable debug logging
DEBUG=* npm run dev
```

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Firebase Authentication](https://firebase.google.com/docs/auth)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

---

**Built with ❤️ using Next.js, Tailwind CSS, and Firebase**
