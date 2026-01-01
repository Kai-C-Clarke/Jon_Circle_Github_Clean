# THE CIRCLE APP

A personal memory preservation application that helps you capture, organize, and preserve your life stories with AI-assisted features.

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![Flask 3.0](https://img.shields.io/badge/Flask-3.0.3-green.svg)
![License](https://img.shields.io/badge/license-Private-red.svg)

## 🌟 Features

- **Memory Capture**: Write and voice-record your life stories
- **AI-Powered**:
  - Automatic memory categorization (DeepSeek AI)
  - Intelligent search across your memories
  - AI-generated biography from your memories
- **Media Management**: Upload and link photos/videos to memories
- **Beautiful PDFs**: Generate magazine-style biography PDFs with photo layouts
- **Timeline View**: See your life story chronologically
- **Privacy-First**: Single-user application, your data stays private

## 📋 Prerequisites

- Python 3.11 or higher
- DeepSeek API key (for AI features) - [Get one here](https://platform.deepseek.com/api_keys)
- Anthropic API key (optional, for Claude features) - [Get one here](https://console.anthropic.com/)

## 🚀 Local Development Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Jon_Circle_Github_Clean
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

Required configuration in `.env`:
```bash
FLASK_SECRET_KEY=your-secret-key-here
DEEPSEEK_API_KEY=your-deepseek-api-key
```

### 5. Initialize Database

The database will be created automatically on first run:

```bash
python app.py
```

### 6. Access the Application

Open your browser to: **http://localhost:5000**

## 🌐 Deploying to Render

### Quick Deploy

1. **Fork/Push this repository to GitHub**

2. **Connect to Render:**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`

3. **Set Environment Variables:**

   In Render Dashboard → Environment, add:

   ```bash
   APP_USERNAME=guypalmer
   APP_PASSWORD=<your-secure-password>
   DEEPSEEK_API_KEY=<your-api-key>
   ANTHROPIC_API_KEY=<your-api-key>
   ```

4. **Update CORS:**

   After first deployment, update `ALLOWED_ORIGINS` in Render Dashboard:
   ```
   https://your-app-name.onrender.com
   ```

5. **Deploy!**

   Click "Apply" and Render will build and deploy your app.

### Important Notes for Render

- **Starter Plan Required**: The free tier has ephemeral storage. You need the Starter plan ($7/month) for the persistent disk to store your database and uploads.
- **Database Location**: The persistent disk is mounted at `/var/data`
- **First Deploy**: Takes 5-10 minutes
- **Auto-deploy**: Enabled by default when you push to your branch

## 🔐 Security

### Authentication

The app uses **HTTP Basic Authentication** for single-user access:
- Set `APP_USERNAME` and `APP_PASSWORD` in environment variables
- The browser will prompt for credentials when accessing protected pages
- Authentication is required for `/app` and all `/api/*` routes (except `/api/health`)
- Landing page (`/`) and goodbye page remain public
- To disable auth for local development: set `DISABLE_AUTH=true` in `.env`

### Privacy Considerations

⚠️ **AI Services**: When using AI features, your memories are sent to:
- **DeepSeek** (for categorization, search, biography generation)
- **Anthropic/Claude** (optional, for additional AI features)

These services process your data according to their privacy policies. If privacy is a concern:
- Review their privacy policies
- Consider self-hosted AI alternatives
- Disable AI features if preferred

### API Keys

**Never commit API keys to Git!**
- All secrets go in `.env` (which is gitignored)
- Use Render's environment variable management
- Rotate keys periodically

## 📁 Project Structure

```
Jon_Circle_Github_Clean/
├── app.py                      # Main Flask application
├── database.py                 # Database initialization
├── pdf_generator.py            # PDF generation (Memory Archive)
├── biography_pdf_generator.py  # Magazine-style biography PDFs
├── ai_search.py               # AI-powered search
├── ai_photo_matcher.py        # AI photo suggestions
├── utils.py                   # Utility functions
├── security_config.py         # Security settings
├── logger_config.py           # Logging configuration
├── templates/                 # HTML templates
│   ├── index.html            # Main app interface
│   ├── landing.html          # Landing page
│   └── goodbye.html          # Exit page
├── static/                    # Static assets
│   ├── css/
│   └── js/
├── uploads/                   # User uploads (gitignored)
├── logs/                      # Application logs (gitignored)
├── requirements.txt           # Python dependencies
├── Procfile                   # Render/Heroku deployment
├── render.yaml                # Render Blueprint configuration
└── .env.example               # Environment template
```

## 🔧 Configuration

### Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `FLASK_SECRET_KEY` - Flask session encryption (required)
- `DEEPSEEK_API_KEY` - DeepSeek AI API key (required for AI features)
- `ANTHROPIC_API_KEY` - Anthropic/Claude API key (optional)
- `APP_USERNAME` - HTTP Basic Auth username (e.g., "guypalmer")
- `APP_PASSWORD` - HTTP Basic Auth password (plain text, secured via HTTPS)
- `DISABLE_AUTH` - Set to "true" to disable auth (development only)
- `ALLOWED_ORIGINS` - CORS allowed origins
- `DATABASE_PATH` - Database file location
- `UPLOAD_FOLDER` - Upload directory location

## 🧪 Testing

Run the test suite:

```bash
# Note: Tests are currently written for the non-existent auth system
# Main app functionality should be tested manually
python app.py
# Then test in browser
```

## 📊 Database Schema

The app uses SQLite with the following main tables:

- `user_profile` - User's basic information
- `memories` - Memory text, dates, categories
- `media` - Uploaded photos/videos
- `memory_media` - Links between memories and media
- `audio_transcriptions` - Voice recordings
- `comments` - Love notes/comments on memories

## 🎨 Features in Detail

### Memory Capture
- Write memories with rich text
- Voice record memories (converted to text)
- Automatic categorization by life phase/theme
- Fuzzy date parsing (e.g., "Summer 1985", "1960s")

### AI Features
- **Smart Search**: Natural language search across memories
- **Auto-categorization**: Memories sorted into childhood, education, work, family, etc.
- **Biography Generation**: AI writes a flowing narrative from your memories
- **Photo Matching**: Suggests photos for each memory based on dates and content

### PDF Export
- **Memory Archive**: Chronological PDF with all memories and photos
- **Biography**: Magazine-style narrative PDF with photo layouts
- Professional layouts with pull quotes and image grids

## 🐛 Troubleshooting

### Database Issues
- **Database not found**: Check `DATABASE_PATH` environment variable
- **Database locked**: Only one process can write at a time
- **Data lost after redeploy**: Ensure persistent disk is enabled on Render

### Upload Issues
- **File too large**: Default limit is 50MB (configurable)
- **Upload folder permission denied**: Check folder permissions
- **Uploads disappear**: Ensure `UPLOAD_FOLDER` is on persistent disk

### AI Features Not Working
- **DeepSeek API errors**: Check API key and credits
- **Biography generation fails**: Check logs for specific error
- **Search not working**: Verify `DEEPSEEK_API_KEY` is set

### Authentication Issues
- **Can't log in**: Verify `APP_PASSWORD_HASH` matches your password
- **Session expires quickly**: Check `FLASK_SECRET_KEY` is consistent

## 📝 Development Notes

### Known Issues
- `auth.py` imports `database_improved.py` which doesn't exist (unused code)
- `test_app.py` tests non-existent auth system
- Several utility scripts in root directory should be organized

### Future Enhancements
- Mobile-responsive design improvements
- Bulk photo upload
- Export to Word/EPUB
- Family member collaboration (multi-user)
- Automated backups to cloud storage

## 🤝 Contributing

This is a private/personal project. For modifications:
1. Create a feature branch
2. Test thoroughly locally
3. Create pull request with description

## 📄 License

Private use only. Not licensed for public distribution.

## 🆘 Support

For issues or questions:
1. Check this README
2. Review `.env.example` for configuration
3. Check Render logs for deployment issues
4. Review `AUTHENTICATION_GUIDE.md` for auth details (if implementing full auth)

## 📮 Contact

Created for Guy Palmer's personal memory preservation.

---

**Version**: 1.0.0
**Last Updated**: 2025-12-31
**Python**: 3.11+
**Framework**: Flask 3.0.3
