import os
from werkzeug.utils import secure_filename
from typing import Dict, Any
import logging

class FileHandler:
    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder
        self.allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        self.logger = logging.getLogger(__name__)
        
        # Ensure upload directory exists
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def handle_image_upload(self, file, product_name: str) -> Dict[str, Any]:
        """Handle image upload for a product"""
        try:
            if not file:
                return {'success': False, 'message': '没有选择文件'}
            
            if file.filename == '':
                return {'success': False, 'message': '没有选择文件'}
            
            if not self.allowed_file(file.filename):
                return {'success': False, 'message': '文件格式不支持'}
            
            # Generate secure filename
            filename = secure_filename(f"{product_name}.jpg").replace(' ', '_')
            filepath = os.path.join(self.upload_folder, filename)
            
            # Save file
            file.save(filepath)
            
            return {
                'success': True,
                'filepath': filepath.replace('\\', '/'),
                'message': '文件上传成功'
            }
            
        except Exception as e:
            self.logger.error(f"Error uploading file: {str(e)}")
            return {'success': False, 'message': f'上传失败: {str(e)}'}
    
    def delete_file(self, filepath: str) -> bool:
        """Delete a file safely"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting file {filepath}: {str(e)}")
            return False
    
    def get_file_size(self, filepath: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(filepath)
        except Exception:
            return 0