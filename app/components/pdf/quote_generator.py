import os
import io
import base64
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

class QuoteGenerator:
    def __init__(self, output_dir="app/static/quotes"):
        """
        Initialize the quote generator.
        
        Args:
            output_dir: Directory where generated quotes will be saved
        """
        self.output_dir = output_dir
        
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize styles
        self.styles = self._create_styles()
    
    def _create_styles(self):
        """Create and return a stylesheet for the PDF."""
        styles = getSampleStyleSheet()
        
        # Adding custom styles
        styles.add(ParagraphStyle(
            name='CenterBold',
            parent=styles['Heading2'],
            alignment=1,  # 1 = center aligned
        ))
        
        styles.add(ParagraphStyle(
            name='Bold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
        ))
        
        styles.add(ParagraphStyle(
            name='BoldRight',
            parent=styles['Normal'],
            alignment=2,  # 2 = right aligned
            fontName='Helvetica-Bold',
        ))
        
        styles.add(ParagraphStyle(
            name='RightAlign',
            parent=styles['Normal'],
            alignment=2,  # 2 = right aligned
        ))
        
        styles.add(ParagraphStyle(
            name='Small',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
        ))
        
        styles.add(ParagraphStyle(
            name='SmallBold',
            parent=styles['Normal'],
            fontSize=8,
            fontName='Helvetica-Bold'
        ))
        
        # Enhance the heading style for the text logo
        styles.add(ParagraphStyle(
            name='LogoHeading',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.darkblue,
            spaceAfter=12,
            fontName='Helvetica-Bold',
        ))
        
        return styles
    
    def generate_quote_pdf(self, quote_data, line_items, pricing_engine):
        """
        Generate a PDF quote.
        
        Args:
            quote_data: Dictionary containing quote details
            line_items: List of line items
            pricing_engine: Instance of PricingEngine to calculate totals
            
        Returns:
            str: Path to the generated PDF file
        """
        # Create a filename using the quote reference
        reference = quote_data.get('quote_reference', f"QU-{datetime.now().strftime('%Y%m%d')}")
        pdf_filename = f"{reference}.pdf"
        pdf_path = os.path.join(self.output_dir, pdf_filename)
        
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Set up the document with A4 page size
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=1.5*cm,
            rightMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        
        # List to hold the flowable elements
        elements = []
        
        # Add the header with logo and company information
        header_elements = self._create_header(quote_data)
        elements.extend(header_elements)
        
        # Add quote information
        quote_info_elements = self._create_quote_info(quote_data)
        elements.extend(quote_info_elements)
        
        # Add line items table
        line_items_elements = self._create_line_items_table(line_items, pricing_engine, quote_data)
        elements.extend(line_items_elements)
        
        # Add terms and conditions
        terms_elements = self._create_terms(quote_data)
        elements.extend(terms_elements)
        
        # Build the PDF document
        doc.build(elements)
        
        # Get the PDF content from the buffer
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Save the PDF to file
        with open(pdf_path, 'wb') as f:
            f.write(pdf_content)
        
        return pdf_path, pdf_content
    
    def _create_header(self, quote_data):
        """Create the header section with logo and company information."""
        elements = []
        
        # Try to use the logo from the images folder
        logo_path = "app/static/images/inkstitchpress_logo.png"
        
        # Default to text-based logo initially
        use_text_logo = True
        logo = None
        
        # Try to load the image logo if it exists
        if os.path.exists(logo_path) and os.path.getsize(logo_path) > 100:  # Ensure it's not empty
            try:
                # In case of any error with image loading, we'll catch all exceptions
                # and fall back to text logo
                logo = Image(logo_path, width=5*cm, height=2*cm)
                use_text_logo = False
            except Exception as e:
                print(f"Error loading logo: {str(e)}")
                use_text_logo = True
                
        # Use text-based logo if image loading failed or file doesn't exist
        if use_text_logo:
            logo_text = "InkStitchPress"
            logo_para = Paragraph(f'<font color="white" size="18">{logo_text}</font>', self.styles['LogoHeading'])
            
            # Create a background color for the logo in a table cell
            logo_table = Table([[logo_para]], colWidths=[9*cm], rowHeights=[1.8*cm])
            logo_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.darkblue),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
            ]))
            logo = logo_table
        
        # Create QUOTE heading for right side with right alignment style
        quote_style = ParagraphStyle(
            name='QuoteHeading',
            parent=self.styles['CenterBold'],
            alignment=2,  # 2 = right aligned
            fontSize=16,
        )
        quote_para = Paragraph("QUOTE", quote_style)
        
        # Create a table for the header with logo on left, QUOTE on right
        header_data = [
            [logo, quote_para]
        ]
        
        header_table = Table(header_data, colWidths=[13*cm, 5*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (0, 0), 'TOP'),
            ('VALIGN', (1, 0), (1, 0), 'TOP'),  # Align QUOTE to top
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('LEFTPADDING', (1, 0), (1, 0), 0), 
            ('RIGHTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (1, 0), (1, 0), 0),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),  # Right-align QUOTE
            ('TOPPADDING', (1, 0), (1, 0), 5),   # Add some padding at the top for QUOTE
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 3*mm))  # Reduced from 5mm to 3mm
        
        # Company info - place directly at left margin
        company_info = [
            Paragraph(quote_data.get('company_name', 'Ink Stitch Press Ltd'), self.styles['Heading3']),
            Paragraph(quote_data.get('company_address_line1', 'Unit C8, Seedbed'), self.styles['Normal']),
            Paragraph(quote_data.get('company_address_line2', 'Business Centre'), self.styles['Normal']),
            Paragraph(quote_data.get('company_address_line3', 'Vanguard Way'), self.styles['Normal']),
            Paragraph(f"{quote_data.get('company_address_line4', 'Shoeburyness')}", self.styles['Normal']),
            Paragraph(f"{quote_data.get('company_postcode', 'SS3 9QY')}", self.styles['Normal'])
        ]
        
        # Add company address elements directly to the flow with no additional styling
        # This will place them at the left margin of the document
        for line in company_info:
            elements.append(line)
        
        elements.append(Spacer(1, 5*mm))  # Reduced from 10mm to 5mm
        
        return elements
    
    def _create_quote_info(self, quote_data):
        """Create the quote information section."""
        elements = []
        
        # Customer and quote details
        customer_name = quote_data.get('customer_name', '')
        quote_date = quote_data.get('quote_date', datetime.now().strftime('%d %b %Y'))
        expiry_date = quote_data.get('expiry_date', '')
        quote_number = quote_data.get('quote_reference', '')
        
        # Format dates if they're in ISO format
        if isinstance(quote_date, str) and len(quote_date) == 10 and quote_date[4] == '-' and quote_date[7] == '-':
            quote_date = datetime.strptime(quote_date, '%Y-%m-%d').strftime('%d %b %Y')
        
        if isinstance(expiry_date, str) and len(expiry_date) == 10 and expiry_date[4] == '-' and expiry_date[7] == '-':
            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').strftime('%d %b %Y')
        
        # Create a better aligned table for customer info and quote details
        # Left column with customer name
        customer_col = Paragraph(f"<b>{customer_name}</b>", self.styles['Normal'])
        
        # Right column with date, expiry, quote number
        date_info = [
            Paragraph(f"<b>Date</b>", self.styles['Normal']),
            Paragraph(f"{quote_date}", self.styles['Normal']),
            Paragraph(f"<b>Expiry</b>", self.styles['Normal']),
            Paragraph(f"{expiry_date}", self.styles['Normal']),
            Paragraph(f"<b>Quote Number</b>", self.styles['Normal']),
            Paragraph(f"{quote_number}", self.styles['Normal'])
        ]
        
        # Create a table with empty cells for spacing/alignment
        empty_cell = Paragraph("", self.styles['Normal'])
        info_data = [
            [empty_cell, empty_cell, customer_col, empty_cell, date_info]
        ]
        
        # Use appropriate column widths to move content to the right
        colWidths = [1*cm, 5*cm, 5*cm, 3*cm, 4*cm]
        info_table = Table(info_data, colWidths=colWidths)
        
        # Style the table for better alignment
        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            # Set alignment for customer name (left align in its cell)
            ('ALIGN', (2, 0), (2, 0), 'LEFT'),
            # Set alignment for date info (right align in its cell)
            ('ALIGN', (4, 0), (4, 0), 'RIGHT'),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 5*mm))  # Reduced from 10mm to 5mm
        
        return elements
    
    def _create_line_items_table(self, line_items, pricing_engine, quote_data):
        """Create the table of line items."""
        elements = []
        
        # Define the column headers
        headers = ["Description", "Quantity", "Unit Price", "Discount", "Amount GBP"]
        
        # Create header rows with Paragraph objects for better styling
        header_row = [Paragraph(h, self.styles['Bold']) for h in headers]
        
        # Prepare the data rows
        data = [header_row]
        
        # Keep track of all rows including main items
        all_row_indices = []
        current_row = 1  # Start after header row
        
        # Add line items
        for item in line_items:
            # Check if the item has printing or embroidery
            has_printing = item.get("has_printing", False)
            has_embroidery = item.get("has_embroidery", False)
            
            # Format the description with decoration details
            product_name = item.get('product_name', item.get('product_group', 'Unknown'))
            primary_category = item.get('primary_category', 'N/A')
            size_range = item.get('size_range', 'N/A')
            description = f"{product_name} - {primary_category} - {size_range}"
            
            # Add decoration details if present
            if has_printing or has_embroidery:
                decoration_details = []
                
                if has_printing:
                    printing_name = item.get("printing_service_name", "Printing")
                    decoration_details.append(f"{printing_name}")
                
                if has_embroidery:
                    embroidery_name = item.get("embroidery_service_name", "Embroidery")
                    decoration_details.append(f"{embroidery_name}")
                
                if decoration_details:
                    description += f"<br/><i>With: {' & '.join(decoration_details)}</i>"
            
            # Check for legacy service-only items
            is_service = item.get("is_service", False)
            
            if is_service:
                service_type = item.get("service_type", "")
                service_name = item.get("service_name", "Unknown Service")
                description = f"{service_type.capitalize()}: {service_name}"
            
            # Add the row with carefully formatted values and consistent types
            data.append([
                Paragraph(description, self.styles['Normal']),  # Use Paragraph for wrapping
                Paragraph(str(int(item['quantity'])), self.styles['Normal']),
                Paragraph(f"£{item['unit_price']:.2f}", self.styles['Normal']),
                Paragraph(f"{item['discount_percent']}%", self.styles['Normal']),
                Paragraph(f"£{item['total_price']:.2f}", self.styles['Normal'])
            ])
            
            # Store the main item row index
            all_row_indices.append(current_row)
            current_row += 1
            
            # We're removing the breakdown lines for base garment and logo costs
        
        # Calculate totals
        # Use the sum of total_price directly instead of recalculating
        subtotal = sum(item.get('total_price', 0) for item in line_items)
        
        # Calculate the sum of unit prices * quantity (for reference only)
        gross_total = sum(item.get('unit_price', 0) * item.get('quantity', 0) for item in line_items)
        
        # Calculate the discount amount
        discount_amount = gross_total - subtotal
        
        # Check if VAT applies
        vat_registered = quote_data.get('vat_registered', False)
        vat_rate = quote_data.get('vat_rate', 20.0) if vat_registered else 0.0
        vat_amount = subtotal * (vat_rate / 100) if vat_registered else 0.0
        
        total = subtotal + vat_amount
        
        # Create empty cells for the footer rows
        empty_cell = Paragraph("", self.styles['Normal'])
        
        # Create subtotal row
        subtotal_label = Paragraph("Subtotal", self.styles['Normal'])
        subtotal_value = Paragraph(f"£{subtotal:.2f}", self.styles['Normal'])
        data.append([empty_cell, empty_cell, empty_cell, subtotal_label, subtotal_value])
        
        # Add VAT row if applicable
        if vat_registered:
            vat_label = Paragraph(f"VAT ({vat_rate:.1f}%)", self.styles['Normal'])
            vat_value = Paragraph(f"£{vat_amount:.2f}", self.styles['Normal'])
            data.append([empty_cell, empty_cell, empty_cell, vat_label, vat_value])
        
        # Add total row with proper bold formatting
        total_label = Paragraph("TOTAL GBP", self.styles['Bold'])
        total_value = Paragraph(f"£{total:.2f}", self.styles['BoldRight'])
        data.append([empty_cell, empty_cell, empty_cell, total_label, total_value])
        
        # Create the table with appropriate column widths
        colWidths = [9*cm, 2*cm, 2.5*cm, 2.5*cm, 2.5*cm]
        table = Table(data, colWidths=colWidths, repeatRows=1)
        
        # Style the table
        style = TableStyle([
            # Headers
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Common styling for all cells
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Draw outer border around entire table
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            
            # Grid lines for header
            ('BOX', (0, 0), (-1, 0), 0.5, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
            
            # Line item alignment
            ('ALIGN', (0, 1), (0, -4), 'LEFT'),       # Description column
            ('ALIGN', (1, 1), (-1, -4), 'RIGHT'),     # Numeric columns
        ])
        
        # Add gridlines for all cells in the table up to the footer
        footer_start = current_row
        for i in range(1, footer_start):
            style.add('LINEBELOW', (0, i), (-1, i), 0.5, colors.black)
            for col in range(1, 5):  # 5 columns (0 to 4)
                style.add('LINEBEFORE', (col, i), (col, i), 0.5, colors.black)
                
        # Footer rows (totals)
        style.add('ALIGN', (-2, footer_start), (-1, -1), 'RIGHT')  # Right align the amount values in total rows
        style.add('LINEABOVE', (-2, footer_start), (-1, footer_start), 1, colors.black)  # Line above subtotal
        style.add('LINEBELOW', (-2, -1), (-1, -1), 1, colors.black)  # Line below total
        style.add('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold')  # Bold font for total row
        
        # Ensure word wrapping for all columns
        style.add('WORDWRAP', (0, 0), (-1, -1), True)
        
        table.setStyle(style)
        elements.append(table)
        elements.append(Spacer(1, 10*mm))
        
        return elements
    
    def _create_terms(self, quote_data):
        """Create the terms and conditions section."""
        elements = []
        
        # Add terms title
        elements.append(Paragraph("Terms", self.styles['Heading3']))
        elements.append(Spacer(1, 5*mm))
        
        # Add terms content
        terms = quote_data.get('terms', [
            "Please note that due to current supply price changes, we can only guarantee our quotations for 30 days from the above-mentioned date, after this, our quote may change.",
            "The client acknowledges that the seller cannot be held responsible for replacing or repairing items supplied by the client that may be damaged during the embroidery or print process."
        ])
        
        for term in terms:
            elements.append(Paragraph(term, self.styles['Normal']))
            elements.append(Spacer(1, 3*mm))
        
        # Add notes if any
        notes = quote_data.get('notes', '')
        if notes:
            elements.append(Spacer(1, 5*mm))
            elements.append(Paragraph("Notes:", self.styles['Heading3']))
            elements.append(Paragraph(notes, self.styles['Normal']))
        
        # Add footer with company registration
        elements.append(Spacer(1, 10*mm))
        company_registration = quote_data.get('company_registration', '')
        elements.append(Paragraph(company_registration, self.styles['Small']))
        
        return elements
    
    def get_quote_as_base64(self, pdf_content):
        """
        Convert PDF content to base64 for embedding in HTML.
        
        Args:
            pdf_content: Raw PDF content
            
        Returns:
            str: Base64 encoded PDF
        """
        return base64.b64encode(pdf_content).decode('utf-8') 