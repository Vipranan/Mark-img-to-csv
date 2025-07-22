"""
Utility functions for the Marksheet AI Agent
"""
import os
import re
from typing import List, Dict, Any
from PIL import Image, ImageEnhance
import io

class ImageProcessor:
    """Utility class for image processing operations"""
    
    @staticmethod
    def enhance_image(image: Image.Image) -> Image.Image:
        """Enhance image quality for better OCR results"""
        try:
            # Convert to RGB if not already
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Enhance contrast
            contrast_enhancer = ImageEnhance.Contrast(image)
            image = contrast_enhancer.enhance(1.2)
            
            # Enhance sharpness
            sharpness_enhancer = ImageEnhance.Sharpness(image)
            image = sharpness_enhancer.enhance(1.1)
            
            return image
            
        except Exception as e:
            print(f"Error enhancing image: {str(e)}")
            return image
    
    @staticmethod
    def resize_image(image: Image.Image, max_size: tuple = (1920, 1080)) -> Image.Image:
        """Resize image if it's too large while maintaining aspect ratio"""
        try:
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            return image
        except Exception as e:
            print(f"Error resizing image: {str(e)}")
            return image

class DataValidator:
    """Utility class for data validation"""
    
    @staticmethod
    def validate_rrn(rrn: str) -> bool:
        """Validate if RRN format looks correct"""
        if not rrn or rrn == "Not Available":
            return False
        
        # Check if it contains alphanumeric characters
        return bool(re.match(r'^[A-Za-z0-9]+$', rrn.strip()))
    
    @staticmethod
    def validate_marks(marks_str: str) -> bool:
        """Validate if marks string contains valid numbers"""
        if not marks_str or marks_str in ["Not Available", "N/A", ""]:
            return False
        
        # Check if it's a valid number or fraction like "85/100"
        patterns = [
            r'^\d+$',  # Just numbers like "85"
            r'^\d+/\d+$',  # Fraction like "85/100"
            r'^\d+\.\d+$',  # Decimal like "85.5"
        ]
        
        return any(re.match(pattern, marks_str.strip()) for pattern in patterns)
    
    @staticmethod
    def clean_numeric_value(value: str) -> str:
        """Clean and extract numeric value from string"""
        if not value:
            return "0"
        
        # Extract numbers from string
        numbers = re.findall(r'\d+(?:\.\d+)?', str(value))
        return numbers[0] if numbers else "0"

class CSVFormatter:
    """Utility class for CSV formatting operations"""
    
    @staticmethod
    def clean_column_name(column_name: str) -> str:
        """Clean column names for CSV compatibility"""
        # Remove special characters and replace with underscore
        cleaned = re.sub(r'[^\w\s]', '', str(column_name))
        # Replace spaces with underscores
        cleaned = re.sub(r'\s+', '_', cleaned)
        # Remove consecutive underscores
        cleaned = re.sub(r'_+', '_', cleaned)
        # Remove leading/trailing underscores
        cleaned = cleaned.strip('_')
        
        return cleaned if cleaned else "Unknown_Field"
    
    @staticmethod
    def format_marks_data(sectionwise_marks: List[Dict[str, Any]]) -> Dict[str, str]:
        """Format section-wise marks data for CSV"""
        formatted_data = {}
        
        if not isinstance(sectionwise_marks, list):
            return formatted_data
        
        for i, subject_data in enumerate(sectionwise_marks):
            if not isinstance(subject_data, dict):
                continue
            
            subject_name = subject_data.get('subject', f'Subject_{i+1}')
            marks_obtained = subject_data.get('marks_obtained', 'N/A')
            max_marks = subject_data.get('max_marks', 'N/A')
            
            # Clean subject name
            clean_subject = CSVFormatter.clean_column_name(subject_name)
            
            formatted_data[f'{clean_subject}_Obtained'] = str(marks_obtained)
            formatted_data[f'{clean_subject}_Maximum'] = str(max_marks)
        
        return formatted_data

class FileManager:
    """Utility class for file management operations"""
    
    @staticmethod
    def ensure_directory(directory_path: str) -> bool:
        """Ensure directory exists, create if it doesn't"""
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {directory_path}: {str(e)}")
            return False
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """Generate a safe filename by removing problematic characters"""
        # Remove or replace problematic characters
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove consecutive underscores
        safe_name = re.sub(r'_+', '_', safe_name)
        # Limit length
        if len(safe_name) > 100:
            name_part = safe_name[:90]
            extension = safe_name[-10:] if '.' in safe_name[-10:] else ''
            safe_name = name_part + extension
        
        return safe_name
    
    @staticmethod
    def get_unique_filename(directory: str, base_filename: str) -> str:
        """Generate a unique filename if file already exists"""
        counter = 1
        filename = base_filename
        name, ext = os.path.splitext(base_filename)
        
        while os.path.exists(os.path.join(directory, filename)):
            filename = f"{name}_{counter}{ext}"
            counter += 1
        
        return filename

# Error handling utilities
class ErrorHandler:
    """Utility class for error handling and logging"""
    
    @staticmethod
    def create_error_response(error_message: str, context: str = "") -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "rrn": "Error",
            "student_name": "Not Available",
            "sectionwise_marks": [],
            "total_marks": "Not Available",
            "error": True,
            "error_message": error_message,
            "context": context
        }
    
    @staticmethod
    def log_error(error: Exception, context: str = ""):
        """Log error with context (can be expanded for proper logging)"""
        print(f"Error in {context}: {type(error).__name__}: {str(error)}")
        
# Constants for validation
COMMON_SUBJECT_NAMES = [
    "Mathematics", "Math", "Science", "English", "Hindi", "Social Studies",
    "Physics", "Chemistry", "Biology", "History", "Geography", "Computer Science",
    "Physical Education", "Art", "Music", "Drawing", "Sanskrit", "Tamil", "Telugu"
]

GRADE_PATTERNS = [
    r'A\+?', r'B\+?', r'C\+?', r'D\+?', r'F',
    r'O', r'A', r'B', r'C', r'D', r'E',  # CBSE grades
    r'[1-9]\d*%',  # Percentage grades
    r'Pass', r'Fail', r'Distinction', r'First Class', r'Second Class'
]