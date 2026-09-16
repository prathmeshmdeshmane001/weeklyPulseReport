# Weekly Review Pulse Dashboard

A simple web dashboard to visualize the AI-powered weekly review pulse pipeline.

## Features

- 📊 **Real-time Status**: View last run, review counts, and next scheduled run
- 📈 **Weekly Pulse**: Display headline summary and key metrics
- 🎯 **Top Themes**: Visualize the 3 most important themes with descriptions
- 💬 **User Quotes**: Show 3 real privacy-safe user quotes
- 💡 **Action Items**: List 3 recommended actions for stakeholders
- 🔄 **Pipeline Status**: Track all 10+ phases of the workflow
- 🔗 **Quick Links**: Direct links to Google Docs and JSON data

## How to Use

### Option 1: Open Local File
Simply open `index.html` in your web browser:
```bash
# On macOS
open dashboard/index.html

# On Windows
start dashboard/index.html

# On Linux
xdg-open dashboard/index.html
```

### Option 2: Serve with Python
```bash
cd dashboard
python -m http.server 8080
# Then open http://localhost:8080
```

### Option 3: GitHub Pages (Recommended)
Deploy to GitHub Pages for a public dashboard:

1. Go to repository Settings → Pages
2. Select "Deploy from a branch"
3. Choose `master` branch and `/dashboard` folder
4. Your dashboard will be at: `https://pbehuray.github.io/m3-weeklyPulseReport/`

## Data Sources

The dashboard fetches data directly from GitHub:
- Weekly Pulse: `phase8/data/weekly_pulse/weekly_pulse.json`
- Validation Report: `phase11/data/validation/phase11_validation_report.json`
- Google Docs Status: `phase9/data/docs_delivery/phase9_delivery_status.json`

## Auto-Refresh

The dashboard automatically refreshes every 5 minutes to show the latest data.

## Customization

Edit `index.html` to customize:
- Colors and styling (CSS in `<style>` section)
- Refresh interval (`REFRESH_INTERVAL` in JavaScript)
- Layout and components (HTML structure)
- Data sources (modify `CONFIG.GITHUB_RAW` URL)

## Screenshots

The dashboard displays:
1. **Header**: Title and description
2. **Status Cards**: Last run, review count, themes, next run
3. **Weekly Pulse**: Headline with links to Google Docs
4. **Themes**: Top 3 themes with descriptions
5. **Quotes**: 3 real user quotes
6. **Actions**: 3 recommended action items
7. **Pipeline**: Visual status of all workflow phases

## Requirements

- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection (to fetch data from GitHub)
- No server required (static HTML file)

## Integration with GitHub Actions

When the weekly workflow runs:
1. New data is generated
2. JSON files are updated
3. Dashboard auto-refreshes
4. Latest insights are displayed

## Troubleshooting

**Dashboard shows "Error loading data"**
- Check if JSON files exist in the repository
- Verify GitHub raw URLs are accessible
- Check browser console for specific errors

**Data is outdated**
- Dashboard refreshes every 5 minutes automatically
- Manual refresh: Press F5 or Ctrl+R

**Links not working**
- Google Docs link requires the document to be published
- Ensure `GDOCS_DOC_ID` secret is configured in GitHub Actions
