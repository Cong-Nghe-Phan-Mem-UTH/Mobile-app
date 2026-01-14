# Hướng dẫn Test iOS

## Cách 1: iOS Simulator (Khuyến nghị cho development)

### Yêu cầu:
- Mac với macOS
- Xcode đã cài đặt (từ App Store)
- Xcode Command Line Tools

### Các bước:

1. **Cài đặt dependencies (nếu chưa):**
```bash
npm install
```

2. **Kiểm tra Xcode đã cài:**
```bash
xcode-select --version
```

3. **Mở iOS Simulator:**
```bash
# Cách 1: Tự động mở khi chạy app
npm run ios

# Cách 2: Mở thủ công
open -a Simulator
```

4. **Chạy app:**
```bash
npm start
# Sau đó nhấn 'i' để mở iOS Simulator
# Hoặc quét QR code bằng Expo Go app
```

## Cách 2: Physical Device (iPhone thật)

### Yêu cầu:
- iPhone với iOS 13.0 trở lên
- Expo Go app (tải từ App Store)
- Máy tính và iPhone cùng mạng WiFi

### Các bước:

1. **Cài Expo Go trên iPhone:**
   - Mở App Store
   - Tìm "Expo Go"
   - Tải và cài đặt

2. **Chạy development server:**
```bash
npm start
```

3. **Kết nối:**
   - Mở Expo Go trên iPhone
   - Quét QR code từ terminal
   - Hoặc nhập URL hiển thị trong terminal

4. **Lưu ý quan trọng:**
   - Nếu backend chạy trên `localhost:4000`, cần đổi sang IP máy tính
   - Tìm IP: `ifconfig | grep "inet "` (macOS/Linux)
   - Sửa trong `src/constants/config.js`:
     ```javascript
     export const API_BASE_URL = 'http://192.168.1.XXX:4000';
     ```

## Troubleshooting

### Lỗi: "Command not found: expo"
```bash
npm install -g expo-cli
# hoặc
npx expo start
```

### Lỗi: "Cannot connect to Metro bundler"
- Đảm bảo backend đang chạy trên port 4000
- Kiểm tra firewall không chặn port
- Thử restart Metro: `npm start -- --reset-cache`

### Lỗi: "Unable to resolve module"
```bash
# Xóa cache và cài lại
rm -rf node_modules
npm install
npm start -- --reset-cache
```

### iOS Simulator không mở được
```bash
# Cài đặt Xcode Command Line Tools
xcode-select --install

# Hoặc mở Xcode và chọn: Xcode > Settings > Locations > Command Line Tools
```

## Quick Start

```bash
# 1. Cài dependencies
npm install

# 2. Chạy app (tự động mở iOS Simulator)
npm run ios

# Hoặc chạy development server
npm start
# Sau đó nhấn 'i' cho iOS
```

