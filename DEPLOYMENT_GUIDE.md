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

### 4. Add Secrets Configuration (Optional)
In the Streamlit Cloud dashboard, go to your app settings and add these secrets (only if you want email functionality):

```toml
# Environment flag (for self-contained app)
DEPLOYED = true

# Email configuration (optional - only needed for quote sending via email)
# EMAIL_HOST = "smtp.gmail.com"
# EMAIL_PORT = 587
# EMAIL_USERNAME = "your-email@gmail.com"
# EMAIL_PASSWORD = "your-app-password"
# EMAIL_FROM = "InkStitchPress <your-email@gmail.com>"
```

**Note: The app now works completely without any secrets! The above is only needed for email functionality.**

### 5. Deploy
- Click "Deploy"
- Wait for the build to complete (usually 2-5 minutes)

## 🎉 What's New in This Version

### Enhanced Features:
- **Self-Contained Data**: 95,882 products included in app (no external dependencies)
- **Enhanced Cost Tracking**: Vehicle costs, depreciation, waste factors, labor tracking
- **Improved Product Selection**: Brand-based filtering with better categorization
- **Cloud-Ready**: Completely self-contained, no external database required

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