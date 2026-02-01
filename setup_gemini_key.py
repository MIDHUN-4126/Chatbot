"""
Secure Gemini API Key Setup
Stores your API key securely in Windows Credential Manager
"""

import keyring
import getpass

SERVICE_NAME = 'TN_Gov_Chatbot'
API_KEY_NAME = 'GEMINI_API_KEY'

def setup_api_key():
    """Setup Gemini API key securely"""
    print("="*60)
    print("Gemini API Key Setup - Secure Storage")
    print("="*60)
    print()
    print("Your API key will be stored securely in Windows Credential Manager")
    print("Get your API key from: https://makersuite.google.com/app/apikey")
    print()
    
    # Check if key already exists
    existing_key = keyring.get_password(SERVICE_NAME, API_KEY_NAME)
    if existing_key:
        print("⚠️ An API key is already stored.")
        choice = input("Do you want to replace it? (yes/no): ").lower()
        if choice not in ['yes', 'y']:
            print("Setup cancelled.")
            return
    
    # Get API key from user
    print()
    api_key = getpass.getpass("Enter your Gemini API key (input hidden): ")
    
    if not api_key or api_key.strip() == '':
        print("❌ Error: API key cannot be empty")
        return
    
    # Store in Windows Credential Manager
    try:
        keyring.set_password(SERVICE_NAME, API_KEY_NAME, api_key)
        print()
        print("✓ API key stored securely!")
        print()
        print("="*60)
        print("Setup Complete!")
        print("="*60)
        print()
        print("Your API key is now stored in Windows Credential Manager")
        print("You can now run: start_server_gemini.bat")
        print()
        print("To view/manage stored credentials:")
        print("  Windows: Control Panel → Credential Manager → Windows Credentials")
        print()
    except Exception as e:
        print(f"❌ Error storing API key: {e}")

def view_stored_key():
    """View if a key is stored (shows only if it exists, not the actual key)"""
    try:
        key = keyring.get_password(SERVICE_NAME, API_KEY_NAME)
        if key:
            print("✓ API key is stored")
            print(f"  First 10 characters: {key[:10]}...")
        else:
            print("❌ No API key found in secure storage")
    except Exception as e:
        print(f"Error: {e}")

def delete_stored_key():
    """Delete the stored API key"""
    try:
        existing_key = keyring.get_password(SERVICE_NAME, API_KEY_NAME)
        if not existing_key:
            print("No API key found to delete")
            return
        
        confirm = input("Are you sure you want to delete the stored API key? (yes/no): ").lower()
        if confirm in ['yes', 'y']:
            keyring.delete_password(SERVICE_NAME, API_KEY_NAME)
            print("✓ API key deleted successfully")
        else:
            print("Deletion cancelled")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    print()
    print("1. Setup/Update API Key")
    print("2. Check if API Key exists")
    print("3. Delete API Key")
    print()
    
    choice = input("Choose an option (1-3): ").strip()
    print()
    
    if choice == '1':
        setup_api_key()
    elif choice == '2':
        view_stored_key()
    elif choice == '3':
        delete_stored_key()
    else:
        print("Invalid choice")
