# Support PM Pulsator - Frontend

A modern, dark-themed React dashboard for visualizing AI-powered app review analysis.

![Dashboard Preview](https://i.imgur.com/your-screenshot.png)

## Features

- 📊 **Real-time Metrics**: Total reviews, categorized count, pending items
- 🎯 **AI Categorization Progress**: Visual progress bar with percentage
- 📱 **Platform Filtering**: All, Android, iOS
- 📅 **Time Period Filters**: Today, Yesterday, Last 7/15/30 Days, Custom Range
- ⭐ **Rating Distribution**: Horizontal bar chart with color-coded ratings
- 💚 **Health Metrics**: NPS score, total reviews, average rating, sentiment split
- 🔍 **Search & Filter**: Search reviews, filter by sentiment
- 🏷️ **Top Themes**: Identified themes with sentiment indicators
- 🌙 **Dark/Light Mode**: Toggle between themes
- 📈 **Interactive Charts**: Built with Recharts

## Tech Stack

- **React 18** - UI framework
- **Recharts** - Data visualization
- **Lucide React** - Icons
- **CSS-in-JS** - Styling (no Tailwind needed for Vercel)

## Quick Start (Local Development)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Open http://localhost:3000
```

## Vercel Deployment Guide

### Step 1: Prepare Your Repository

Make sure your frontend code is in the `frontend/` directory:

```
m3-weeklyPulseReport/
├── frontend/
│   ├── package.json
│   ├── vercel.json
│   ├── README.md
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.js
│       ├── index.js
│       └── index.css
├── .github/
├── phase2-12/
└── ...
```

### Step 2: Install Vercel CLI (Optional)

```bash
# Install Vercel CLI globally
npm i -g vercel

# Login to Vercel
vercel login
```

### Step 3: Deploy to Vercel

#### Option A: Deploy via Vercel CLI

```bash
cd frontend

# Deploy (follow prompts)
vercel

# For production deployment
vercel --prod
```

#### Option B: Deploy via GitHub Integration (Recommended)

1. **Push code to GitHub**:
   ```bash
   git add frontend/
   git commit -m "Add React dashboard frontend"
   git push origin master
   ```

2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Sign up/login with GitHub
   - Click **"Add New Project"**
   - Import your `m3-weeklyPulseReport` repository

3. **Configure Project**:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `build` (default)

4. **Environment Variables** (Optional):
   If you need to set API endpoints:
   - `REACT_APP_API_URL` - Your backend API URL
   - `REACT_APP_GITHUB_RAW` - GitHub raw content URL

5. **Deploy**:
   - Click **"Deploy"**
   - Wait for build to complete (1-2 minutes)
   - Get your live URL: `https://your-project.vercel.app`

### Step 4: Configure Custom Domain (Optional)

1. In Vercel dashboard, go to your project
2. Click **"Settings"** → **"Domains"**
3. Enter your domain (e.g., `pulsator.yourcompany.com`)
4. Follow DNS configuration instructions

### Step 5: Enable Auto-Deployments

Vercel automatically deploys when you push to GitHub:

- **Production Branch**: `master` or `main`
- **Preview Deployments**: Every pull request gets a preview URL

## Connecting to Real Data

Currently, the dashboard uses mock data. To connect to your actual pipeline data:

### Option 1: GitHub Raw Data (No Backend Needed)

Modify `App.js` to fetch from GitHub:

```javascript
const fetchData = async () => {
  setLoading(true);
  try {
    // Fetch from GitHub raw
    const pulseResponse = await fetch(
      'https://raw.githubusercontent.com/pbehuray/m3-weeklyPulseReport/master/phase8/data/weekly_pulse/weekly_pulse.json'
    );
    const pulseData = await pulseResponse.json();
    
    // Transform data for dashboard
    const transformedData = {
      totalReviews: 6792,
      categorized: pulseData.top_themes?.length * 100 || 0,
      themes: pulseData.top_themes?.map(t => ({
        label: t.label,
        count: Math.floor(Math.random() * 200) + 50,
        sentiment: 'mixed'
      })),
      // ... map other fields
    };
    
    setData(transformedData);
  } catch (error) {
    console.error('Error fetching data:', error);
  } finally {
    setLoading(false);
  }
};
```

### Option 2: Create Simple API Endpoint

Create a serverless function in Vercel:

```javascript
// api/data.js
export default async function handler(req, res) {
  // Fetch from GitHub or your database
  const data = await fetch('https://raw.githubusercontent.com/.../weekly_pulse.json');
  const json = await data.json();
  
  res.status(200).json(json);
}
```

## Project Structure

```
frontend/
├── public/
│   ├── index.html          # HTML template
│   └── favicon.ico         # App icon
├── src/
│   ├── App.js              # Main dashboard component
│   ├── index.js            # App entry point
│   └── index.css           # Global styles
├── package.json            # Dependencies & scripts
├── vercel.json             # Vercel configuration
└── README.md               # This file
```

## Available Scripts

- `npm start` - Run development server
- `npm run build` - Create production build
- `npm test` - Run tests
- `vercel` - Deploy to Vercel
- `vercel --prod` - Deploy to production

## Customization

### Colors
Edit the `colors` object in `App.js`:

```javascript
const colors = {
  primary: '#10b981',    // Emerald green
  secondary: '#3b82f6',   // Blue
  warning: '#f59e0b',      // Amber
  danger: '#ef4444',       // Red
  background: '#0f172a',   // Dark slate
  card: '#1e293b',         // Card background
  text: '#f8fafc',         // Text color
  // ...
};
```

### Components

The dashboard has 6 main sections:
1. **Header** - Logo, platform filters, sync button
2. **Reviews Summary** - Total reviews, AI categorization progress
3. **Platform & Time Filters** - Filter controls
4. **Rating Distribution** - Bar chart + stats
5. **Health Metrics** - NPS, sentiment, key stats
6. **Top Themes** - Theme list with sentiment

### Adding New Tabs

Add to `navItems` array in `App.js`:

```javascript
const navItems = [
  { id: 'reviews', label: 'Reviews', icon: MessageSquare },
  { id: 'analytics', label: 'Analytics', icon: PieChart },
  // Add your new tab:
  { id: 'insights', label: 'Insights', icon: Lightbulb },
];
```

## Environment Variables

Create `.env.local` for local development:

```
REACT_APP_API_URL=https://api.yourservice.com
REACT_APP_GITHUB_RAW=https://raw.githubusercontent.com/pbehuray/m3-weeklyPulseReport/master
REACT_APP_REFRESH_INTERVAL=300000
```

## Troubleshooting

**Build fails on Vercel**
- Check `package.json` has all dependencies
- Ensure `vercel.json` root directory is correct
- Check build logs in Vercel dashboard

**Charts not rendering**
- Ensure `recharts` is in package.json
- Check for responsive container width/height

**Dark mode not working**
- Check CSS variables are properly defined
- Ensure `darkMode` state is managed correctly

**Data not loading**
- Check browser console for CORS errors
- Verify GitHub raw URLs are accessible
- Check network tab for failed requests

## Next Steps

1. ✅ Deploy to Vercel
2. 🔌 Connect to real data (GitHub API or your backend)
3. 📱 Test on mobile devices
4. 🔐 Add authentication (if needed)
5. 📊 Add more visualizations
6. 🔔 Add real-time notifications

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [React Documentation](https://react.dev)
- [Recharts Examples](https://recharts.org/en-US/examples)

## License

MIT - Same as parent project
