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
from dropbox import DropboxOAuth2FlowNoRedirect
import plotly.io as pio

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
        print(f"Attempting to access path: {path}")  # Debug print
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
        print(f"Error accessing path {path}: {e}")
        # Try listing the root to see what's available
        try:
            root_contents = dbx.files_list_folder("")
            print("\nAvailable root folders:")
            for entry in root_contents.entries:
                print(f"- {entry.path_display}")
        except Exception as root_error:
            print(f"Error listing root: {root_error}")
    
    return image_files

def get_dropbox_client():
    """
    Initialize Dropbox client with access token from environment variable
    
    Returns:
        dropbox.Dropbox: Initialized Dropbox client or None if initialization fails
    """
    try:
        # Get access token from environment variable instead of file
        access_token = os.getenv('DROPBOX_ACCESS_TOKEN')
        if not access_token:
            raise ValueError("DROPBOX_ACCESS_TOKEN environment variable not set")
            
        # Initialize Dropbox with access token
        dbx = dropbox.Dropbox(access_token)
        return dbx
    except Exception as e:
        print(f"Error initializing Dropbox client: {str(e)}")
        return None

def display_random_photo(folder_path="/Photos"):
    """
    Display four random photos from the specified Dropbox folder
    
    Args:
        folder_path (str): Path to the folder containing photos in Dropbox
    """
    try:
        # Initialize Dropbox client
        dbx = get_dropbox_client()
        if not dbx:
            return
        
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
            
            # Add annotations for each image with larger text and better spacing
            fig.add_annotation(
                text=os.path.basename(image_path),
                xref=f'x{idx+1}' if idx > 0 else 'x',
                yref=f'y{idx+1}' if idx > 0 else 'y',
                x=0.5,
                y=-0.15,  # First line position
                showarrow=False,
                font=dict(size=6.5, color='gray'),
                align='center'
            )
            fig.add_annotation(
                text=f"Created: {created_date}<br>Modified: {modified_date}",  # Split onto separate lines
                xref=f'x{idx+1}' if idx > 0 else 'x',
                yref=f'y{idx+1}' if idx > 0 else 'y',
                x=0.5,
                y=-0.35,  # Moved down further for second line
                showarrow=False,
                font=dict(size=6.5, color='gray'),
                align='center'
            )
        
        # Update layout with larger bottom margin to accommodate text
        fig.update_layout(
            template="plotly_dark",
            grid=dict(rows=2, columns=2, pattern='independent'),
            showlegend=False,
            paper_bgcolor='rgb(17,17,17)',
            plot_bgcolor='rgb(17,17,17)',
            margin=dict(l=0, r=0, t=30, b=100),  # Increased bottom margin for more text space
            # Remove all axis labels and ticks
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, visible=False),
            xaxis2=dict(showticklabels=False, showgrid=False, zeroline=False, visible=False),
            xaxis3=dict(showticklabels=False, showgrid=False, zeroline=False, visible=False),
            xaxis4=dict(showticklabels=False, showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, visible=False),
            yaxis2=dict(showticklabels=False, showgrid=False, zeroline=False, visible=False),
            yaxis3=dict(showticklabels=False, showgrid=False, zeroline=False, visible=False),
            yaxis4=dict(showticklabels=False, showgrid=False, zeroline=False, visible=False)
        )
        
        # Save the figure to a temporary HTML file
        temp_file = "temp_plot.html"
        pio.write_html(fig, temp_file, auto_open=False)
        print(f"\nPlotly figure saved to: {os.path.abspath(temp_file)}")
        print("Open this file in your browser to view the photos")

    except dropbox.exceptions.AuthError:
        print("Authentication failed. Please check your access token.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Example folder path - users should modify this for their use case
    folder_path = "/your_photos_folder"
    display_random_photo(folder_path=folder_path)
