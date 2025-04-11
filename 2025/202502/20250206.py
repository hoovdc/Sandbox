# photos_dropbox_get_standalone.py
#initial version by Claude 3.5 Sonnet
import dropbox
import random
import tempfile
from PIL import Image
import os
import plotly.graph_objects as go
from io import BytesIO
import json

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
    Display four random photos in a 2x2 grid from the specified Dropbox folder using Plotly
    
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
        
        # Select 4 random images
        random_images = random.sample(image_files, min(4, len(image_files)))
        
        # Create figure with 2x2 subplots
        fig = go.Figure()
        
        # Calculate positions for 2x2 grid
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        
        for idx, image_path in enumerate(random_images):
            # Download the file to memory
            _, response = dbx.files_download(image_path)
            image_data = response.content
            
            # Open image using PIL
            img = Image.open(BytesIO(image_data))
            
            # Convert image to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Get file metadata for dates
            file_metadata = dbx.files_get_metadata(image_path)
            created_date = file_metadata.client_modified.strftime("%Y-%m-%d %H:%M:%S")
            modified_date = file_metadata.server_modified.strftime("%Y-%m-%d %H:%M:%S")
            
            # Add image to figure with domain coordinates
            row, col = positions[idx]
            fig.add_trace(go.Image(
                z=img,
                xaxis=f'x{idx+1}' if idx > 0 else 'x',
                yaxis=f'y{idx+1}' if idx > 0 else 'y'
            ))
            
            # Add annotations for each image
            fig.add_annotation(
                text=os.path.basename(image_path),
                xref=f'x{idx+1}' if idx > 0 else 'x',
                yref=f'y{idx+1}' if idx > 0 else 'y',
                x=0.5,
                y=-0.05,
                showarrow=False,
                font=dict(size=5, color='gray'),
                align='center'
            )
            fig.add_annotation(
                text=f"Created: {created_date} | Modified: {modified_date}",
                xref=f'x{idx+1}' if idx > 0 else 'x',
                yref=f'y{idx+1}' if idx > 0 else 'y',
                x=0.5,
                y=-0.15,
                showarrow=False,
                font=dict(size=5, color='gray'),
                align='center'
            )
        
        # Update layout for 2x2 grid
        fig.update_layout(
            template="plotly_dark",
            grid=dict(rows=2, columns=2, pattern='independent'),
            showlegend=False,
            paper_bgcolor='rgb(17,17,17)',
            plot_bgcolor='rgb(17,17,17)',
            margin=dict(l=0, r=0, t=30, b=50)
        )
        
        # Update all axes to remove grid lines and ticks
        for i in range(1, 5):
            suffix = str(i) if i > 1 else ''
            fig.update_xaxes(showgrid=False, zeroline=False, visible=False, name=f'x{suffix}')
            fig.update_yaxes(showgrid=False, zeroline=False, visible=False, name=f'y{suffix}')
        
        # Show the figure
        fig.show()

    except dropbox.exceptions.AuthError:
        print("Authentication failed. Please check your access token.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Read access token from Dropbox_secrets.json
    try:
        with open(os.path.join(os.path.dirname(__file__), 'Dropbox_secrets.json')) as f:
            secrets = json.load(f)
            ACCESS_TOKEN = secrets['dropbox_access_token']
    except FileNotFoundError:
        print("Error: Dropbox_secrets.json file not found")
        exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in Dropbox_secrets.json")
        exit(1)
    except KeyError:
        print("Error: 'dropbox_access_token' not found in Dropbox_secrets.json")
        exit(1)
    
    # Call the function
    display_random_photo(ACCESS_TOKEN)
