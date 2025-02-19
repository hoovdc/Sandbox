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
import plotly.io as pio
import time

def get_all_photos_recursive(dbx, path, max_files=80, timeout_seconds=30):
    """
    Recursively get all photo files from Dropbox folder and subfolders
    with timeout and file limit safeguards
    """
    start_time = time.time()
    image_files = []
    try:
        print(f"Scanning path: {path}")
        
        # Add timeout check for initial API call
        initial_api_start_time = time.time()
        try:
            result = dbx.files_list_folder(path, limit=100)
            print(f"Initial API call completed in {time.time() - initial_api_start_time:.2f} seconds")
        except Exception as e:
            print(f"Error in initial API call: {str(e)}")
            if time.time() - initial_api_start_time > 10:  # 10 seconds timeout for initial call
                print("Timeout occurred during initial API call")
            return image_files
        
        # Known photo file extensions (most common only)
        photo_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', 
                          '.webp', '.heic', '.heif', '.raw', '.cr2', '.nef', 
                          '.arw', '.dng')
        files_processed = 0
        
        while True:
            for entry in result.entries:
                # Check timeout
                if time.time() - start_time > timeout_seconds:
                    print(f"Timeout after {timeout_seconds} seconds")
                    return image_files

                files_processed += 1
                print(f"Processing file {files_processed}: {entry.path_display}")
                
                # Check file limit
                if files_processed >= max_files:
                    print(f"Reached maximum file limit of {max_files}")
                    return image_files
                
                if isinstance(entry, dropbox.files.FileMetadata):
                    if any(entry.path_lower.endswith(ext) for ext in photo_extensions):
                        image_files.append(entry.path_display)
                        print(f"Found image ({len(image_files)}): {entry.path_display}")
                
                # Only process immediate files, skip subfolders for now
                # elif isinstance(entry, dropbox.files.FolderMetadata):
                #     subfolder_files = get_all_photos_recursive(
                #         dbx, entry.path_display, 
                #         max_files - files_processed,
                #         timeout_seconds - (time.time() - start_time)
                #     )
                #     image_files.extend(subfolder_files)
            
            if result.has_more:
                print("Loading more files...")
                result = dbx.files_list_folder_continue(result.cursor)
            else:
                break
                
            # Add a check to break the loop if we've exceeded the timeout
            if time.time() - start_time > timeout_seconds:
                print(f"Timeout after {timeout_seconds} seconds")
                return image_files
                
    except dropbox.exceptions.ApiError as e:
        print(f"Dropbox API Error: {e}")
        if hasattr(e, 'error') and hasattr(e.error, 'is_path'):
            print(f"Path error details: {e.error}")
    except Exception as e:
        print(f"Error accessing path {path}: {e}")
        
    print(f"Found {len(image_files)} images in {path}")
    return image_files

def get_dropbox_client():
    """Initialize Dropbox client with automatic token refresh"""
    # This is a placeholder function. In a real application, you would need to implement
    # proper authentication and token management.
    return dropbox.Dropbox("mock_access_token")

def display_random_photo(folder_path="/Photos"):
    """
    Display four random photos from the specified Dropbox folder
    
    Args:
        folder_path (str): Path to the folder containing photos in Dropbox
    """
    try:
        print("Initializing Dropbox client...")
        dbx = get_dropbox_client()
        if not dbx:
            return
        
        print("Getting list of photos...")
        image_files = get_all_photos_recursive(dbx, folder_path, max_files=80, timeout_seconds=30)
        
        if not image_files:
            print("No image files found in the specified folder")
            return
        
        print(f"Found total of {len(image_files)} images")
        print("Selecting random images...")
        
        random_images = random.sample(image_files, min(4, len(image_files)))
        
        fig = go.Figure()
        
        print("Processing selected images...")
        start_time = time.time()
        
        # Define positions for the 2x2 grid
        positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
        
        for idx, image_path in enumerate(random_images):
            print(f"Processing image {idx+1}/{len(random_images)}: {image_path}")
            
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
            print(f"Added image {idx+1} to figure")
            
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
                text=f"Created: {created_date}<br>Modified: {modified_date}",
                xref=f'x{idx+1}' if idx > 0 else 'x',
                yref=f'y{idx+1}' if idx > 0 else 'y',
                x=0.5,
                y=-0.35,
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
        
        # Save the figure to a temporary HTML file with minimal dependencies
        temp_file = "temp_plot.html"
        pio.write_html(
            fig, 
            temp_file, 
            auto_open=False,
            include_plotlyjs='CDN',
            full_html=True
        )
        print(f"\nPlotly figure saved to: {os.path.abspath(temp_file)}")
        print("Open this file in your browser to view the photos")

        # Check if the process took too long
        if time.time() - start_time > 30:  # 30 seconds timeout
            print("Warning: Image processing took longer than expected. Consider optimizing the code.")

    except dropbox.exceptions.AuthError:
        print("Authentication failed. Please check your access token.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Use the correct folder path that we can see exists
    app_folder_path = "/Pictures_CopiesForDashAppTesting"
    display_random_photo(folder_path=app_folder_path)
