import streamlit as st
import hashlib
import hmac

def check_password(username, password):
    """
    Check if the username and password match the stored credentials.
    """
    # Create a hash of the expected password
    # This is better than storing in plain text, but for production
    # you would want a more secure approach
    def make_hash(password):
        return hashlib.sha256(str.encode(password)).hexdigest()
    
    # Get stored password hash from secrets
    stored_users = {
        "Kelly": make_hash("JUBS")
    }
    
    # Check if the username exists and the password matches
    if username in stored_users:
        return hmac.compare_digest(stored_users[username], make_hash(password))
    return False

def login_form():
    """
    Display a login form and handle authentication.
    Returns True if the user is logged in, False otherwise.
    """
    # If the user is already authenticated, return True
    if st.session_state.get("authenticated", False):
        return True
    
    # Set the title of the login form
    st.title("InkStitchPress Pricer - Login")
    
    # Display the login form
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if check_password(username, password):
                st.session_state.authenticated = True
                # Need to rerun the app after successful login
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    # Display additional information
    st.info("Please enter your credentials to access the application.")
    
    # Return False as the user is not authenticated yet
    return False 