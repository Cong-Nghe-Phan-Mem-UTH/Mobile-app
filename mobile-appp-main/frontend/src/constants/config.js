// API Configuration
// Development: 
// - Emulator/Simulator: use 'http://localhost:4000'
// - Physical device: use your computer's IP (e.g., 'http://192.168.1.100:4000')
//   Find your IP: macOS/Linux: `ifconfig` or `ipconfig` on Windows
export const API_BASE_URL = __DEV__ 
  ? 'http://localhost:4000' // Change to your computer's IP when testing on physical device
  : 'https://api.bigboy.com'; // Replace with production URL

export const API_VERSION = '/api/v1';

// Storage Keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  USER_DATA: 'user_data',
  GUEST_TOKEN: 'guest_token',
  TABLE_TOKEN: 'table_token',
};

// Membership Tiers
export const MEMBERSHIP_TIERS = {
  IRON: 'Sắt',
  SILVER: 'Bạc',
  GOLD: 'Vàng',
  DIAMOND: 'Kim cương',
};

// Order Status
export const ORDER_STATUS = {
  PENDING: 'pending',
  CONFIRMED: 'confirmed',
  PREPARING: 'preparing',
  READY: 'ready',
  SERVED: 'served',
  CANCELLED: 'cancelled',
};

// Colors
export const COLORS = {
  primary: '#FF6B35',
  secondary: '#F7931E',
  background: '#FFFFFF',
  surface: '#F5F5F5',
  text: '#212121',
  textSecondary: '#757575',
  error: '#D32F2F',
  success: '#388E3C',
  warning: '#F57C00',
  info: '#1976D2',
  border: '#E0E0E0',
};

