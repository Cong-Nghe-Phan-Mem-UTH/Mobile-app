# BigBoy Mobile App

React Native mobile application for BigBoy restaurant management SaaS platform.

## Features

- 🔐 Authentication (Login/Register)
- 🏪 Restaurant Discovery & Search
- 📱 QR Code Scanner for Menu Access
- 🍽️ Menu Browsing & Ordering
- 🛒 Shopping Cart
- ⭐ Reviews & Ratings
- 📅 Table Reservations
- 👤 User Profile & History
- 💎 Membership Tiers

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Run on iOS:
```bash
npm run ios
```

4. Run on Android:
```bash
npm run android
```

## Configuration

Update API base URL in `src/constants/config.js`:
```javascript
export const API_BASE_URL = 'http://localhost:4000'; // or your production URL
```

## Project Structure

```
src/
├── screens/          # Screen components
│   ├── auth/        # Authentication screens
│   ├── restaurants/ # Restaurant screens
│   ├── menu/        # Menu & ordering screens
│   ├── orders/      # Order screens
│   ├── reviews/     # Review screens
│   ├── reservations/# Reservation screens
│   ├── profile/     # Profile screens
│   └── qr/          # QR scanner screen
├── services/        # API services
├── store/           # State management (Zustand)
├── navigation/      # Navigation setup
└── constants/       # Constants & config
```

## Dependencies

- React Native & Expo
- React Navigation
- Zustand (State Management)
- Axios (API calls)
- AsyncStorage (Local storage)
- React Native Paper (UI components)
- Expo Camera (QR Scanner)
- React Native Vector Icons

## API Integration

The app integrates with the BigBoy backend API at `http://localhost:4000/api/v1`.

All API endpoints are documented in the service files under `src/services/`.

## License

Private - BigBoy Platform

