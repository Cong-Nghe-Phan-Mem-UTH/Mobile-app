# 🚀 Quick Start - Test iOS

## Bước 1: Cài đặt dependencies (nếu chưa)
```bash
npm install
```

## Bước 2: Chạy app trên iOS

### Option A: iOS Simulator (Mac + Xcode)
```bash
npm run ios
```
Lệnh này sẽ:
- Tự động mở iOS Simulator
- Build và chạy app

### Option B: Development Server (cho cả Simulator và Device)
```bash
npm start
```
Sau đó:
- Nhấn `i` để mở iOS Simulator
- Hoặc quét QR code bằng Expo Go app trên iPhone

## Bước 3: Đảm bảo Backend đang chạy
Backend cần chạy trên `http://localhost:4000` (hoặc IP máy tính nếu test trên device thật)

## Lưu ý khi test trên iPhone thật:

1. **Cài Expo Go:**
   - Tải từ App Store: "Expo Go"

2. **Đổi API URL:**
   - Tìm IP máy tính: `ifconfig | grep "inet "`
   - Sửa `src/constants/config.js`:
   ```javascript
   export const API_BASE_URL = 'http://192.168.1.XXX:4000';
   ```

3. **Quét QR code:**
   - Mở Expo Go
   - Quét QR code từ terminal

## Troubleshooting

**Lỗi "Cannot find module":**
```bash
rm -rf node_modules
npm install
```

**iOS Simulator không mở:**
- Cài Xcode từ App Store
- Chạy: `xcode-select --install`

**Metro bundler lỗi:**
```bash
npm start -- --reset-cache
```

