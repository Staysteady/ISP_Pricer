# Cloud Setup Instructions

To properly configure the app for the Streamlit Cloud environment, you need to add an `IS_CLOUD` flag to your secrets.

1. Go to your Streamlit Cloud dashboard
2. Select your app (InkStitchPress Pricer)
3. Click on "Settings" in the sidebar
4. Scroll down to "Secrets"
5. Add the following to your secrets:

```toml
IS_CLOUD = true
```

This will tell the app it's running in the cloud environment, allowing it to disable PDF preview (which doesn't work in the cloud) and show the enhanced download button instead.

## What This Change Does

This configuration tells the app to:
- Skip trying to render PDF previews directly in the browser when running in the cloud
- Display a more prominent download button instead
- Show an informative message explaining why the preview isn't available

The PDF generation and download functionality will continue to work as before. 