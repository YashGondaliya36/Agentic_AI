# 🌐 Web UI for Smart Email Assistant

**Beautiful, modern web interface built with FastAPI + HTML/CSS/JS**

## 🎨 Features

- ✅ **Glassmorphism Design** - Premium, modern UI
- ✅ **Animated Background** - Floating gradient orbs
- ✅ **Real-time Updates** - Instant email processing
- ✅ **Responsive** - Works on all devices
- ✅ **Fast API** - Async backend
- ✅ **Interactive Modals** - Smooth animations
- ✅ **Toast Notifications** - Beautiful alerts

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd project_04_smart_email_assistant
pip install -r requirements.txt
pip install -r requirements-web.txt
```

### 2. Run the Web Server

```bash
# From web directory
cd web
python app.py
```

Or use `uvicorn`:
```bash
cd web
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 3. Open Browser

```
http://localhost:8000
```

## 📁 Structure

```
web/
├── app.py                 # FastAPI backend
├── templates/
│   └── index.html         # Main dashboard
└read static/
    ├── css/
    │   └── style.css      # Glassmorphism design
    └── js/
        └── app.js         # Frontend logic
```

## 🎯 How It Works

### Backend (FastAPI)

**Endpoints:**
- `GET /` - Main dashboard
- `GET /api/emails` - Fetch emails
- `POST /api/classify/{id}` - Classify email
- `POST /api/generate-draft/{id}` - Generate response
- `POST /api/send-email` - Send email
- `POST /api/archive/{id}` - Archive email

### Frontend

**Features:**
- Email grid with cards
- Click email → Open modal
- Classify → AI categorization
- Generate Draft → AI response
- Edit draft → Human-in-loop
- Send → Confirmation & send
- Archive → Mark as read

## 💡 User Flow

```
1. Open Dashboard
   ↓
2. See Unread Emails (Grid View)
   ↓
3. Click Email Card
   ↓
4. Modal Opens with Details
   ↓
5. Click "Classify Email"
   → Shows: Category, Priority
   ↓
6. Click "Generate Draft"
   → AI writes response
   ↓
7. Edit Draft (if needed)
   ↓
8. Click "Send Email"
   → Confirmation → Send
   ↓
9. Email Sent ✅
   → Original marked as read
   → Removed from grid
```

## 🎨 Design Features

### Glassmorphism
- Frosted glass effect
- Backdrop blur
- Semi-transparent backgrounds
- Smooth borders

### Animations
- Floating gradient orbs
- Card hover effects
- Modal slide-up
- Toast notifications
- Button ripple effects

### Colors
- **Primary**: #6366f1 (Indigo)
- **Secondary**: #8b5cf6 (Purple)
- **Success**: #10b981 (Green)
- **Danger**: #ef4444 (Red)

### Typography
- **Font**: Inter (Google Fonts)
- **Headings**: 700 weight
- **Body**: 400 weight
- **Buttons**: 500 weight

## 🔧 Customization

### Change Colors

Edit `web/static/css/style.css`:
```css
:root {
    --primary: #your-color;
    --secondary: #your-color;
}
```

### Change Layout

Grid columns in `style.css`:
```css
.email-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
}
```

### Add Features

1. Edit `web/app.py` - Add endpoint
2. Edit `web/static/js/app.js` - Add function
3. Edit `web/templates/index.html` - Add UI element

## 📊 API Response Format

### GET /api/emails
```json
{
    "success": true,
    "emails": [...],
    "count": 5
}
```

### POST /api/classify/{id}
```json
{
    "success": true,
    "category": "important",
    "priority": 4,
    "action_required": true
}
```

### POST /api/generate-draft/{id}
```json
{
    "success": true,
    "draft": "Email response text...",
    "category": "normal",
    "priority": 3
}
```

## 🚀 Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker web.app:app
```

### Using Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
```bash
export GOOGLE_API_KEY=your_key
export PORT=8000
```

## 🎉 Features Showcase

### Real-time Stats
- Email count badge
- Processed count badge
- Auto-updates

### Human-in-Loop
- Review every draft
- Edit before sending
- Skip unwanted emails
- Full control

### Smart Categorization
- Urgent
- Important
- Normal
- Promotional
- Spam

## 📱 Responsive Design

- **Desktop**: 3-column grid
- **Tablet**: 2-column grid
- **Mobile**: 1-column stack

## ✅ Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 🔒 Security

- CORS configured
- Input sanitization
- XSS protection
- CSRF tokens (add if needed)

---

**Built with ❤️ using FastAPI, Modern HTML/CSS/JS**
