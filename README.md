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

The application uses SQLite to store product data, quotes, and cost information. The database is created automatically on first run.

## License

This project is proprietary and not licensed for redistribution. 