# blob_storage.py
# Vercel Blob Storage utility for handling file uploads

import os
import io
from typing import Optional
import time
from vercel_storage import blob

class VercelBlobStorage:
    def __init__(self):
        self.token = os.getenv('BLOB_READ_WRITE_TOKEN')
        
        if not self.token:
            raise ValueError("BLOB_READ_WRITE_TOKEN environment variable is required")
    
    def upload_file(self, file_data: bytes, filename: str, content_type: str = 'application/octet-stream') -> Optional[str]:
        """
        Upload a file to Vercel Blob Storage
        
        Args:
            file_data: The file content as bytes
            filename: The desired filename
            content_type: MIME type of the file
            
        Returns:
            The public URL of the uploaded file, or None if upload failed
        """
        try:
            # Create a unique filename to avoid conflicts
            timestamp = int(time.time())
            unique_filename = f"{timestamp}_{filename}"
            
            # Upload to Vercel Blob Storage using the official SDK
            result = blob.put(
                pathname=unique_filename,
                body=file_data,
                options={
                    'token': self.token,
                    'contentType': content_type
                }
            )
            
            return result.get('url') if result else None
                
        except Exception as e:
            print(f"Error uploading to blob storage: {e}")
            return None
    
    def delete_file(self, url: str) -> bool:
        """
        Delete a file from Vercel Blob Storage
        
        Args:
            url: The public URL of the file to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            result = blob.delete(
                url=url,
                options={'token': self.token}
            )
            
            return result is not None
            
        except Exception as e:
            print(f"Error deleting from blob storage: {e}")
            return False
    
    def upload_image(self, image_file, user_id: int, prefix: str = "image") -> Optional[str]:
        """
        Upload an image file with automatic content type detection
        
        Args:
            image_file: Flask file object
            user_id: User ID for organizing files
            prefix: Prefix for the filename (e.g., 'profile', 'post')
            
        Returns:
            The public URL of the uploaded image, or None if upload failed
        """
        try:
            # Read file data
            file_data = image_file.read()
            
            # Determine content type based on file extension
            filename = image_file.filename.lower()
            if filename.endswith('.jpg') or filename.endswith('.jpeg'):
                content_type = 'image/jpeg'
                ext = '.jpg'
            elif filename.endswith('.png'):
                content_type = 'image/png'
                ext = '.png'
            elif filename.endswith('.gif'):
                content_type = 'image/gif'
                ext = '.gif'
            elif filename.endswith('.webp'):
                content_type = 'image/webp'
                ext = '.webp'
            else:
                # Default to JPEG for unknown types
                content_type = 'image/jpeg'
                ext = '.jpg'
            
            # Create filename
            unique_filename = f"{prefix}_{user_id}_{int(time.time())}{ext}"
            
            return self.upload_file(file_data, unique_filename, content_type)
            
        except Exception as e:
            print(f"Error uploading image: {e}")
            return None
    
    def list_files(self, prefix: Optional[str] = None) -> list:
        """
        List files in Vercel Blob Storage
        
        Args:
            prefix: Optional prefix to filter files
            
        Returns:
            List of file information
        """
        try:
            options = {'token': self.token}
            if prefix:
                options['prefix'] = prefix
                
            result = blob.list(options=options)
            return result.get('blobs', []) if result else []
            
        except Exception as e:
            print(f"Error listing files: {e}")
            return []


# Global instance
blob_storage = None

def get_blob_storage():
    """Get or create the blob storage instance"""
    global blob_storage
    
    # Check if we're in an environment with blob storage configured
    if os.getenv('BLOB_READ_WRITE_TOKEN'):
        if blob_storage is None:
            try:
                blob_storage = VercelBlobStorage()
            except Exception as e:
                print(f"Failed to initialize blob storage: {e}")
                return None
        return blob_storage
    else:
        return None

def is_blob_storage_available():
    """Check if blob storage is available"""
    return get_blob_storage() is not None 