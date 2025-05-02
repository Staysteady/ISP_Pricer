# InkStitchPress Pricer

A comprehensive pricing and quoting tool for InkStitchPress, a printing and embroidery business. This application manages product catalogs, pricing calculations, service offerings, and generates professional quotes.

## Features

- **Product Selection**: Browse and filter products from supplier catalogs
- **Dynamic Pricing**: Apply markups, quantity discounts, and service charges
- **Quote Generation**: Create, save, and export professional quotations
- **Cost Tracking**: Monitor profitability and business expenses
- **PDF Generation**: Export quotes as PDF documents

## Requirements

- Python 3.8+
- Streamlit
- Pandas
- Other dependencies listed in requirements.txt

## Installation

1. Clone this repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

1. Upload a product price list Excel file (or use the default if available)
2. Configure markup settings and discount rules
3. Set up printing and embroidery services
4. Browse products and create quotes
5. Generate PDF quotes and track costs

## Database

The application supports two database modes:
- **Local mode**: Uses SQLite database stored locally
- **Cloud mode**: Uses Supabase PostgreSQL database for web deployment

## Deployment

### Local Deployment

For local development and testing:
1. Clone the repository
2. Install dependencies with `pip install -r requirements.txt`
3. Run with `streamlit run app.py`

### Cloud Deployment (Streamlit Cloud)

1. **Set up Supabase:**
   - Create a Supabase account at [supabase.com](https://supabase.com)
   - Create a new project
   - Run the SQL migration scripts from the `supabase/migrations` directory
   - Get your project URL and anon key

2. **Deploy to Streamlit Cloud:**
   - Fork this repository on GitHub
   - Sign up at [streamlit.io/cloud](https://streamlit.io/cloud)
   - Connect your GitHub repository
   - In the Streamlit Cloud dashboard, add the following secrets:
     ```
     DEPLOYED = true
     SUPABASE_URL = "https://your-project-id.supabase.co"
     SUPABASE_KEY = "your-supabase-anon-key"
     ```
   - Deploy your app

3. **Initial Database Setup:**
   - Once deployed, upload your price list Excel file via the app interface
   - The data will be stored in your Supabase database

## License

This project is proprietary and not licensed for redistribution. 