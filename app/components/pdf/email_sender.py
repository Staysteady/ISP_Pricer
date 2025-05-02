import os
import subprocess
import platform
import tempfile
import shutil

class EmailSender:
    def __init__(self, from_email="enquiries@inkstitchpress.co.uk"):
        """
        Initialize the email sender.
        
        Args:
            from_email: The sender's email address
        """
        self.from_email = from_email
    
    def send_email_with_pdf(self, to_email, subject, body, pdf_path, customer_name):
        """
        Send an email with the quote PDF attached.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            pdf_path: Path to the PDF file to attach
            customer_name: Customer name for the email body
            
        Returns:
            bool: True if successful, False otherwise
            str: Success or error message
        """
        try:
            # Check if the PDF file exists
            if not os.path.exists(pdf_path):
                return False, f"PDF file not found at {pdf_path}"
            
            # Make sure the path is absolute
            pdf_path = os.path.abspath(pdf_path)
            
            # Use the default mail client on macOS
            if platform.system() == 'Darwin':  # macOS
                return self._send_email_macos(to_email, subject, body, pdf_path)
            else:
                return False, "Unsupported operating system. Currently, only macOS is supported for email sending."
        except Exception as e:
            return False, f"Error sending email: {str(e)}"
    
    def _send_email_macos(self, to_email, subject, body, pdf_path):
        """
        Send an email using the macOS Mail app.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            pdf_path: Path to the PDF file to attach
            
        Returns:
            bool: True if successful, False otherwise
            str: Success or error message
        """
        try:
            # Make sure we have a valid PDF path
            if not os.path.exists(pdf_path):
                return False, f"PDF file not found at {pdf_path}"
            
            # Create a temporary copy of the PDF to avoid permission issues
            temp_dir = tempfile.mkdtemp()
            temp_pdf_path = os.path.join(temp_dir, os.path.basename(pdf_path))
            shutil.copy2(pdf_path, temp_pdf_path)
            
            # Create a temporary AppleScript file
            with tempfile.NamedTemporaryFile(suffix='.applescript', delete=False) as script_file:
                script_path = script_file.name
                
                # Make sure the paths are properly escaped for AppleScript
                escaped_pdf_path = temp_pdf_path.replace('\\', '\\\\').replace('"', '\\"')
                escaped_body = body.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                
                # AppleScript to create and send an email with attachment
                applescript = f'''
                tell application "Mail"
                    set newMessage to make new outgoing message with properties {{subject:"{subject}", content:"{escaped_body}", visible:true}}
                    tell newMessage
                        set sender to "{self.from_email}"
                        make new to recipient at end of to recipients with properties {{address:"{to_email}"}}
                        
                        # Add attachment
                        tell content of newMessage
                            try
                                make new attachment with properties {{file name:"{escaped_pdf_path}"}} at after last paragraph
                            on error errMsg
                                display dialog "Error attaching file: " & errMsg
                            end try
                        end tell
                        
                        # Uncomment the next line to automatically send without showing the compose window
                        # send
                    end tell
                    activate
                end tell
                '''
                
                script_file.write(applescript.encode('utf-8'))
            
            # Run the AppleScript
            result = subprocess.run(['osascript', script_path], capture_output=True, text=True)
            
            # Clean up the temporary script file and PDF copy
            try:
                os.unlink(script_path)
                os.unlink(temp_pdf_path)
                os.rmdir(temp_dir)
            except Exception as e:
                print(f"Warning: Failed to clean up temporary files: {e}")
            
            if result.returncode == 0:
                return True, "Email compose window opened with PDF attached. Please review and send."
            else:
                return False, f"Error creating email: {result.stderr}"
        
        except Exception as e:
            return False, f"Error sending email via macOS Mail: {str(e)}"
    
    def generate_email_body(self, quote_data, customer_name):
        """
        Generate a standard email body for quote emails.
        
        Args:
            quote_data: Dictionary containing quote details
            customer_name: Customer name to personalize the email
            
        Returns:
            str: Formatted email body
        """
        quote_ref = quote_data.get('quote_reference', '')
        expiry_date = quote_data.get('expiry_date', '')
        
        # Format expiry date if it's in ISO format
        if isinstance(expiry_date, str) and len(expiry_date) == 10 and expiry_date[4] == '-' and expiry_date[7] == '-':
            from datetime import datetime
            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').strftime('%d %b %Y')
        
        body = f"""Dear {customer_name},

Thank you for your inquiry. Please find attached your quote (Ref: {quote_ref}).

This quote is valid until {expiry_date}.

If you have any questions or would like to proceed, please don't hesitate to contact us.

Kind regards,

Ink Stitch Press Team
enquiries@inkstitchpress.co.uk
"""
        
        return body 