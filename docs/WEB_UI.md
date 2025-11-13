# Web UI Documentation

## Overview

The Trailer-to-Campaign Autopilot includes a modern web interface that makes it easy to generate marketing campaigns without using the command line. The web UI provides real-time progress tracking, campaign management, and a clean interface to view generated content.

## Features

- **🎬 Campaign Generation**: Submit trailer URLs and generate complete campaigns
- **📊 Real-time Progress**: Watch as your campaign is built step-by-step
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **🎨 Modern UI**: Clean, gradient-based design with Tailwind CSS
- **💾 Campaign Management**: View and manage previously generated campaigns
- **🤖 AI Integration**: Displays AI-enhanced content when Gemini is configured
- **📈 Analytics**: View engagement metrics, sentiment analysis, and trend data

## Installation

### Prerequisites

Ensure you have completed the main setup in [QUICKSTART.md](QUICKSTART.md):

1. Python 3.8+ installed
2. API keys configured in `.env` file
3. Core dependencies installed

### Install Web Dependencies

```bash
pip install flask>=2.3.0
```

Or install all dependencies including Flask:

```bash
pip install -r requirements.txt
```

## Launching the Web UI

### Start the Server

From the project root directory:

```bash
python web/app.py
```

You should see output like:

```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### Access the Interface

Open your web browser and navigate to:

```
http://localhost:5000
```

## Using the Web UI

### 1. Generate a Campaign

1. **Enter Trailer URL**: Paste a YouTube trailer URL (e.g., `https://www.youtube.com/watch?v=VIDEO_ID`)
2. **Specify Movie Title**: Enter the movie title (e.g., "Dune: Part Two")
3. **Target Regions** (optional): Enter regions separated by commas (e.g., "US,UK,IN")
4. **Click "Generate Campaign"**: The system will start processing

### 2. Track Progress

Watch the real-time progress indicator as the system:

- ✅ **Fetches Metadata**: Gets movie info from TMDb
- ✅ **Analyzes Engagement**: Retrieves YouTube comments and views
- ✅ **Runs Sentiment**: Analyzes audience sentiment
- ✅ **Checks Trends**: Gathers Google Trends data
- ✅ **Generates Copy**: Creates ad copy variants
- ✅ **AI Enhancement**: Enhances content with Gemini (if configured)

Progress updates every second with detailed status messages.

### 3. View Results

Once complete, you'll automatically be redirected to the results page showing:

#### Movie Information
- Title, genres, runtime, release date
- Cast and director
- TMDb rating

#### Key Metrics
- 📺 **Views**: Total YouTube trailer views
- 💬 **Comments**: Number of comments analyzed
- 😊 **Sentiment**: Overall sentiment score (0-100%)
- 🎯 **Top Region**: Highest-priority market

#### Campaign Content (Tabbed View)

**Ad Copy Tab**
- AI-enhanced variants (when Gemini is configured)
- Template-based variants
- Grounded in actual metrics

**Social Media Tab**
- Platform-specific posts for:
  - Twitter/𝕏
  - Instagram
  - Facebook
  - TikTok

**Rollout Plan Tab**
- Phased regional strategy
- Budget allocation per phase
- Timeline and target regions
- Recommended activities

**AI Insights Tab** (when Gemini is configured)
- 🟢 **Opportunities**: Strategic advantages
- 🟡 **Risks**: Potential challenges
- 🔵 **Recommendations**: Actionable suggestions

### 4. Manage Campaigns

Click **"Recent Campaigns"** in the header to:
- View all generated campaigns
- Load previous campaign results
- Access campaign JSON files

## API Endpoints

The web UI exposes a RESTful API:

### Health Check
```
GET /health
```
Returns: `{"status": "ok"}`

### Configuration Status
```
GET /api/config
```
Returns API configuration status and AI provider information.

### Generate Campaign
```
POST /api/generate
Content-Type: application/json

{
  "trailer_url": "https://youtube.com/watch?v=...",
  "movie_title": "Dune: Part Two",
  "regions": ["US", "UK", "IN"]
}
```
Returns: `{"job_id": "unique-job-id"}`

### Check Status
```
GET /api/status/<job_id>
```
Returns:
```json
{
  "status": "in_progress",
  "progress": 50,
  "message": "Analyzing sentiment...",
  "step": "sentiment"
}
```

Status values:
- `pending`: Job queued
- `in_progress`: Currently processing
- `completed`: Successfully finished
- `failed`: Error occurred

### List Campaigns
```
GET /api/campaigns
```
Returns list of campaign filenames from `outputs/` directory.

### Get Campaign Data
```
GET /api/campaign/<filename>
```
Returns full campaign JSON.

### View Campaign in UI
```
GET /view/<filename>
```
Renders campaign in the web interface.

## Configuration

### Port Configuration

By default, the server runs on port `5000`. To change this, edit `web/app.py`:

```python
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
```

### Debug Mode

Debug mode is enabled by default for development. For production, set:

```python
app.run(debug=False)
```

### Environment Variables

The web UI uses the same `.env` file as the CLI:

```bash
# Required
TMDB_API_KEY=your_key_here
YOUTUBE_API_KEY=your_key_here

# Optional (for AI enhancement)
GEMINI_API_KEY=your_key_here

# Optional (TMDb v4 token)
TMDB_BEARER_TOKEN=your_token_here
```

## Troubleshooting

### Server Won't Start

**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solution**: Install Flask:
```bash
pip install flask
```

### Port Already in Use

**Error**: `Address already in use`

**Solution**: Either:
1. Kill the process using port 5000:
   ```bash
   lsof -ti:5000 | xargs kill
   ```
2. Change the port in `web/app.py`

### Campaign Generation Fails

**Check**:
1. API keys are configured in `.env`
2. CLI command works: `python main.py generate --url <trailer_url>`
3. Check browser console for JavaScript errors
4. Check Flask terminal output for Python errors

### Progress Not Updating

**Check**:
1. Browser console for fetch errors
2. Network tab shows `/api/status/<job_id>` requests
3. Job ID is valid in the status endpoint

### AI Enhancement Not Showing

**Check**:
1. `GEMINI_API_KEY` is set in `.env`
2. Config check shows Gemini as available:
   ```bash
   python main.py config-check
   ```
3. Results page shows "AI Insights" tab

## Architecture

### Backend (app.py)

- **Flask Web Server**: Serves HTML templates and API endpoints
- **Background Processing**: Uses threading for async campaign generation
- **Status Tracking**: In-memory job status dictionary
- **File Management**: Reads/writes campaigns to `outputs/` directory

### Frontend (Templates)

- **base.html**: Navigation, layout, modals
- **index.html**: Campaign generation form with real-time progress
- **results.html**: Tabbed campaign display with metrics

### Styling

- **Tailwind CSS**: Utility-first CSS framework (loaded via CDN)
- **Gradient Themes**: Purple-to-pink gradients for modern look
- **Responsive Grid**: Mobile-first responsive design

### JavaScript

- **Async Form Submission**: Prevents page reload
- **Status Polling**: 1-second interval for progress updates
- **Tab Navigation**: Client-side tab switching
- **Auto-redirect**: Navigates to results when complete

## Performance

### Campaign Generation Time

Typical timeline (varies by API response times):
- Metadata: 1-2 seconds
- Engagement: 2-3 seconds
- Sentiment: 1-2 seconds
- Trends: 3-5 seconds (or skipped if rate limited)
- Ad Copy: 1-2 seconds
- AI Enhancement: 3-5 seconds (if Gemini configured)

**Total**: ~12-20 seconds per campaign

### Concurrent Requests

The current implementation processes campaigns sequentially. For multiple users:
- Jobs are queued in memory
- Each job processed in a background thread
- Status tracked by unique job_id

### Scaling Considerations

For production use, consider:
- **Task Queue**: Use Celery/Redis for distributed processing
- **Database**: Store campaigns in PostgreSQL instead of JSON files
- **Load Balancer**: Use Gunicorn/uWSGI with multiple workers
- **Caching**: Cache TMDb metadata, sentiment models
- **Rate Limiting**: Add rate limits to prevent API quota exhaustion

## Security Notes

### Production Deployment

⚠️ **The current setup is for development only**. For production:

1. **Disable Debug Mode**:
   ```python
   app.run(debug=False)
   ```

2. **Use Production Server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 web.app:app
   ```

3. **Add Authentication**: Protect endpoints with user auth
4. **Use HTTPS**: Configure SSL certificates
5. **Environment Variables**: Never commit `.env` to version control
6. **Input Validation**: Sanitize trailer URLs and user inputs
7. **Rate Limiting**: Use Flask-Limiter to prevent abuse

## Browser Compatibility

Tested and working on:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

Requires JavaScript enabled for full functionality.

## Screenshots

### Home Page
Clean form interface with progress tracking and feature highlights.

### Results Page
Comprehensive campaign display with metrics, ad copy, social posts, rollout plan, and AI insights.

### Recent Campaigns
Modal showing previously generated campaigns for quick access.

## Related Documentation

- [README.md](../README.md): Project overview
- [QUICKSTART.md](QUICKSTART.md): Setup and installation
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md): System architecture
- [SAMPLE_OUTPUT.md](SAMPLE_OUTPUT.md): Example campaign structure

## Support

For issues or questions:
1. Check troubleshooting section above
2. Verify API configuration: `python main.py config-check`
3. Test CLI functionality: `python main.py generate --url <trailer_url>`
4. Check Flask logs in terminal
5. Inspect browser console for JavaScript errors

## Future Enhancements

Potential features for future versions:
- 📥 Download campaign as JSON/PDF
- 📋 Copy-to-clipboard for ad copy
- 📊 Campaign comparison tool
- 🔍 Search/filter past campaigns
- 📈 Analytics dashboard
- 👥 Multi-user support with authentication
- 🎨 Custom branding/themes
- 📧 Email delivery of campaigns
- 🔗 Direct social media publishing
