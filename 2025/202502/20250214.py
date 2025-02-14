def get_GoogleAPI_service() -> Any:
    """Initialize and return Google API service with proper authentication."""
    secrets_dir = os.path.join(os.path.dirname(__file__), 'Folder')
    credentials_path = os.path.join(secrets_dir, 'x.json')
    token_path = os.path.join(secrets_dir, 'y.json')
    scopes = ['https://www.googleapis.com/auth/xx']
    
    creds = None
    try:
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, scopes)
    except Exception as e:
        print(f"Error loading token: {e}")
        creds = None

    try:
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(f"Missing credentials.json file at {credentials_path}")
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, 
                    scopes,
                    redirect_uri='http://localhost:0'
                )
                creds = flow.run_local_server(port=0)
            
            # Save the refreshed/new token
            with open(token_path, 'w', encoding='utf-8') as token:
                token.write(creds.to_json())
    except Exception as e:
        print(f"Error during authentication: {e}")
        raise

    return build('calendar', 'v3', credentials=creds)