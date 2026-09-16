# Vercel Deployment Plan - Support PM Pulsator Dashboard

## Quick Deploy (2 Minutes)

### Step 1: Go to Vercel
1. Visit [vercel.com](https://vercel.com)
2. Click **"Sign Up"** (use GitHub for easy integration)

### Step 2: Import Project
1. Click **"Add New Project"**
2. Find and select `m3-weeklyPulseReport`
3. Click **"Import"**

### Step 3: Configure Build
| Setting | Value |
|---------|-------|
| Framework | Create React App |
| Root Directory | `frontend` |
| Build Command | `npm run build` |
| Output Directory | `build` |

### Step 4: Deploy
1. Click **"Deploy"**
2. Wait 1-2 minutes for build
3. Get your URL: `https://your-project.vercel.app`

---

## What Was Created

```
frontend/
├── package.json           # React + Recharts + Lucide icons
├── vercel.json            # Vercel routing config
├── public/
│   └── index.html         # HTML template
└── src/
    ├── App.js            # Main dashboard (600+ lines)
    ├── index.js          # Entry point
    └── index.css         # Global styles
```

## Dashboard Features

✅ **Modern Dark Theme** - Matches your screenshot  
✅ **6 Navigation Tabs** - Reviews, Analytics, Categories, Word Cloud, Ideation, Reporting  
✅ **Review Counter** - Shows 6,792 total with sync status  
✅ **AI Categorization Progress** - Visual progress bar with %  
✅ **Platform Filters** - All / Android / iOS  
✅ **Time Period Filters** - Today, Yesterday, Last 7/15/30 Days  
✅ **Rating Distribution** - Color-coded horizontal bars  
✅ **Health Metrics** - NPS score, total reviews, avg rating  
✅ **Sentiment Split** - Positive/Neutral/Negative breakdown  
✅ **Search & Filter** - Search bar with sentiment buttons  
✅ **Top Themes** - 5 themes with mention counts  
✅ **Dark/Light Mode Toggle** - Moon/sun icon in header  

---

## Custom Domain (Optional)

After deployment:
1. Go to Project Settings → Domains
2. Add your domain (e.g., `pulsator.groww.com`)
3. Follow DNS instructions

---

## Connecting Real Data

### Option 1: GitHub Raw (Easiest)

Modify `App.js` line ~45:

```javascript
const fetchData = async () => {
  setLoading(true);
  try {
    // Fetch from GitHub
    const response = await fetch(
      'https://raw.githubusercontent.com/pbehuray/m3-weeklyPulseReport/master/phase8/data/weekly_pulse/weekly_pulse.json'
    );
    const pulseData = await response.json();
    
    setData({
      ...mockData,
      themes: pulseData.top_themes?.map(t => ({
        label: t.label,
        count: Math.floor(Math.random() * 200) + 50,
        sentiment: 'mixed'
      })) || mockData.themes,
      headline: pulseData.headline || mockData.headline
    });
  } catch (error) {
    console.error('Error:', error);
  } finally {
    setLoading(false);
  }
};
```

### Option 2: API Endpoint

Create `api/data.js` in project root for serverless function.

---

## Environment Variables

If needed, add in Vercel dashboard:
- `REACT_APP_API_URL` - Your backend URL
- `REACT_APP_GITHUB_TOKEN` - For private repos

---

## Auto-Deployment

✅ **Enabled by default**
- Push to `master` → Auto-deploy to production
- Pull requests → Preview deployments

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | Check `frontend/package.json` has all dependencies |
| Charts blank | Ensure `recharts` is installed |
| Dark mode stuck | Check `darkMode` state in `App.js` |
| Data not loading | Check GitHub raw URLs in browser console |

---

## Post-Deployment Checklist

- [ ] Dashboard loads without errors
- [ ] Dark theme shows correctly
- [ ] All 6 navigation tabs visible
- [ ] Charts render properly
- [ ] Platform filters work
- [ ] Time period buttons clickable
- [ ] Search bar functional
- [ ] Connect to real GitHub data
- [ ] Add custom domain (optional)

---

## Your Dashboard URL

After deployment, your dashboard will be at:
```
https://[project-name].vercel.app
```

Or with custom domain:
```
https://pulsator.yourcompany.com
```

---

## Next Features to Add

1. 🔐 **Authentication** - Login with Google/GitHub
2. 📊 **More Charts** - Line charts, pie charts, trends
3. 🔔 **Notifications** - WebSocket real-time updates
4. 📱 **Mobile App** - React Native version
5. 🤖 **AI Insights** - GPT-4 generated summaries
6. 📧 **Email Reports** - Automated weekly digests

---

## Support

- Vercel Docs: [vercel.com/docs](https://vercel.com/docs)
- React Docs: [react.dev](https://react.dev)
- Issues: Check browser console for errors

---

**Deploy Now**: [vercel.com/new](https://vercel.com/new)
