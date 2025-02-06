# photos_dropbox_get_standalone.py
#initial version by Claude 3.5 Sonnet
import dropbox
import random
import tempfile
from PIL import Image
import os
import plotly.graph_objects as go
from io import BytesIO

def get_all_photos_recursive(dbx, path):
    """
    Recursively get all photo files from Dropbox folder and subfolders
    
    Args:
        dbx: Dropbox client instance
        path (str): Current path to search
    
    Returns:
        list: List of photo file paths
    """
    image_files = []
    try:
        result = dbx.files_list_folder(path)
        
        # Known photo file extensions (lowercase)
        photo_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', 
                          '.webp', '.heic', '.heif', '.raw', '.cr2', '.nef', 
                          '.arw', '.dng')
        
        while True:
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    # Convert path to lowercase for case-insensitive comparison
                    if any(entry.path_lower.endswith(ext) for ext in photo_extensions):
                        image_files.append(entry.path_display)
                elif isinstance(entry, dropbox.files.FolderMetadata):
                    # Recursively search subfolders
                    image_files.extend(get_all_photos_recursive(dbx, entry.path_display))
            
            # Handle pagination for folders with many files
            if result.has_more:
                result = dbx.files_list_folder_continue(result.cursor)
            else:
                break
                
    except Exception as e:
        print(f"Error accessing path {path}: {str(e)}")
    
    return image_files

def display_random_photo(access_token, folder_path="/Photos"):
    """
    Display a random photo from the specified Dropbox folder using Plotly
    
    Args:
        access_token (str): Dropbox access token
        folder_path (str): Path to the folder containing photos in Dropbox
    """
    try:
        # Initialize Dropbox client
        dbx = dropbox.Dropbox(access_token)
        
        # Get all image files recursively
        image_files = get_all_photos_recursive(dbx, folder_path)
        
        if not image_files:
            print("No image files found in the specified folder or its subfolders")
            return
        
        # Select a random image
        random_image = random.choice(image_files)
        print(f"Selected image: {random_image}")
        
        # Download the file to memory
        _, response = dbx.files_download(random_image)
        image_data = response.content
        
        # Open image using PIL
        img = Image.open(BytesIO(image_data))
        
        # Convert image to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Create Plotly figure with dark theme
        fig = go.Figure()
        
        # Add image to figure
        fig.add_trace(go.Image(z=img))
        
        # Update layout for better display with dark theme
        fig.update_layout(
            template="plotly_dark",
            title=os.path.basename(random_image),
            xaxis={'showgrid': False, 'zeroline': False, 'visible': False},
            yaxis={'showgrid': False, 'zeroline': False, 'visible': False},
            margin=dict(l=0, r=0, t=30, b=0),
            paper_bgcolor='rgb(17,17,17)',  # Dark background
            plot_bgcolor='rgb(17,17,17)'    # Dark background
        )
        
        # Show the figure
        fig.show()

    except dropbox.exceptions.AuthError:
        print("Authentication failed. Please check your access token.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Replace with your Dropbox access token
    ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"
    
    # Call the function
    display_random_photo(ACCESS_TOKEN)
