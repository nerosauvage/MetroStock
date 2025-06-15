import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here_change_in_production'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # File upload configuration
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Excel file configuration
    EXCEL_FILE = 'inventory.xlsx'
    
    # Inventory settings
    LOW_STOCK_THRESHOLD = 5
    
    # Pagination
    PRODUCTS_PER_PAGE = 20
    
    @staticmethod
    def init_app(app):
        # Ensure upload directory exists
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)