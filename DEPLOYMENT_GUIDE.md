# InkStitchPress Pricer - Streamlit Cloud Deployment Guide

## 🚀 Ready for Deployment!

Your application has been enhanced and is now completely self-contained with all product data included. Here's how to deploy it to Streamlit Cloud.

## Prerequisites
- GitHub repository: `https://github.com/Staysteady/ISP_Pricer.git`
- All changes committed and pushed ✅
- Self-contained product data included ✅

## Step-by-Step Deployment

### 1. Access Streamlit Cloud
- Go to [share.streamlit.io](https://share.streamlit.io)
- Sign in with your GitHub account

### 2. Create New App
- Click "New app" 
- Select your repository: `Staysteady/ISP_Pricer`
- Set main file path: `app.py`
- Set branch: `main`

### 3. Configure App Settings
- App name: `inkstitchpress-pricer` (or your preferred name)
- App URL will be: `https://inkstitchpress-pricer.streamlit.app`

### 4. Add Secrets Configuration
In the Streamlit Cloud dashboard, go to your app settings and add these secrets:

```toml
# Environment flags
DEPLOYED = true
IS_CLOUD = true

# Supabase connection (for cloud database sync)
SUPABASE_URL = "https://oxgfxjhdguultqqrbwxa.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im94Z2Z4amhkZ3V1bHRxcXJid3hhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYyMTg0MzQsImV4cCI6MjA2MTc5NDQzNH0.IAloyZDavDSkIyat3n9-DweNK65WhttTymfT7VzUqS4"

# Email configuration (optional - for quote sending)
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USERNAME = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
EMAIL_FROM = "InkStitchPress <your-email@gmail.com>"
```

### 5. Deploy
- Click "Deploy"
- Wait for the build to complete (usually 2-5 minutes)

## 🎉 What's New in This Version

### Enhanced Features:
- **Self-Contained Data**: 95,882 products included in app (no external Excel dependency)
- **Enhanced Cost Tracking**: Vehicle costs, depreciation, waste factors, labor tracking
- **Improved Product Selection**: Brand-based filtering with better categorization
- **Cloud-Ready**: Optimized for web deployment with Supabase integration

### User Experience:
- **Login**: Username: `Kelly`, Password: `JUBS`
- **Product Data**: Automatically loads from internal database
- **Cost Analysis**: Enhanced profitability tracking with detailed cost breakdowns
- **PDF Generation**: Full quote generation with download capability

## Troubleshooting

### If deployment fails:
1. Check the logs in Streamlit Cloud dashboard
2. Ensure all secrets are properly configured
3. Verify requirements.txt includes all dependencies

### If app loads but shows errors:
1. Click "Load Default Price List" to initialize product data
2. Check that secrets are correctly formatted (no extra spaces)
3. Verify Supabase connection if using cloud database

## Success Indicators
✅ App loads without errors  
✅ Login works with provided credentials  
✅ Product data loads automatically  
✅ Quote generation and PDF download work  
✅ Cost tracking displays enhanced metrics  

## Support
- Repository: https://github.com/Staysteady/ISP_Pricer
- Streamlit Docs: https://docs.streamlit.io/streamlit-community-cloud