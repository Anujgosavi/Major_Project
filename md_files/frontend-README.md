# AI Ergonomics — React Web Frontend

A modern, responsive React 19 web application for real-time ergonomic monitoring, live video annotation streaming, interactive alert notifications, and historical session reports.

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
npm install
```

### 2. Start the Development Server
```bash
npm start
```
The app will run at `http://localhost:3000`.

---

## 🛠️ Frontend Architecture

### Pages
- **`LandingPage.js` (`/`)**: Product showcase, ergonomic feature breakdown, and quick start CTAs.
- **`Dashboard.js` (`/dashboard`)**: Aggregated metrics, posture score donut chart, weekly bar chart, and recent sessions table.
- **`LiveFeed.js` (`/live`)**: Real-time MJPEG live stream, side-by-side **2-column compact Live Metrics sidebar** (no scroll needed), and interactive notification banners.
- **`Reports.js` (`/reports`)**: Searchable session history, posture score filters, and export triggers.
- **`Login.js` & `Signup.js` (`/login`, `/signup`)**: Glassmorphic auth views with input validation and password strength meters.

### Components
- **`Navbar.js`**: Top navigation with search bar, active link indicators, and quick profile actions.
- **`Sidebar.js`**: Collapsible left sidebar navigation.
- **`Layout.js`**: Standard page wrapper with header, sidebar, and content area.
- **`Footer.js`**: Footer links and copyright.

### Backend Proxy (`setupProxy.js`)
Configures `http-proxy-middleware` to seamlessly route:
- `/api/*` ──► `http://127.0.0.1:5000/api/*`
- `/video_feed` ──► `http://127.0.0.1:5000/video_feed`

---

## 📦 Available Scripts

- `npm start`: Runs the development server on port 3000.
- `npm run build`: Bundles the application for production in `build/`.
- `npm test`: Runs React test suites.
