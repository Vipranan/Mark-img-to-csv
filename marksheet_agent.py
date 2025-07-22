"""
Marksheet AI Agent - Core logic for extracting information from marksheet images
"""
import requests
import base64
import json
import pandas as pd
from typing import Dict, Any, Optional
from PIL import Image
import io
import re
from config import Config

class MarksheetAgent:
    def __init__(self):
        """Initialize the Marksheet Agent with Perplexity API configuration"""
        Config.validate_config()
        self.api_key = Config.PERPLEXITY_API_KEY
        self.base_url = Config.PERPLEXITY_BASE_URL
        self.model = Config.MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def encode_image_to_base64(self, image_file) -> str:
        """Convert uploaded image file to base64 string"""
        try:
            # If it's a file-like object from Streamlit
            if hasattr(image_file, 'read'):
                image_bytes = image_file.read()
                # Reset file pointer if possible
                if hasattr(image_file, 'seek'):
                    image_file.seek(0)
            else:
                image_bytes = image_file
            
            # Validate image
            img = Image.open(io.BytesIO(image_bytes))
            img.verify()
            
            # Convert to base64
            base64_string = base64.b64encode(image_bytes).decode('utf-8')
            return base64_string
        except Exception as e:
            raise ValueError(f"Error processing image: {str(e)}")
    
    def create_extraction_prompt(self) -> str:
        """Create a detailed prompt for extracting marksheet information"""
        prompt = """
        You are an expert AI assistant specialized in extracting information from educational marksheets and report cards.
        
        Please analyze this marksheet image and extract the following information:
        
        1. **RRN (Roll/Registration Number)**: Extract the student's roll number or registration number
        2. **Student Name**: Extract the student's full name
        3. **Section-wise Marks**: Extract marks for each subject/section with subject names
        4. **Total Marks**: Extract the total marks scored
        5. **Maximum Marks**: Extract the maximum possible marks
        6. **Percentage/Grade**: Extract percentage or grade if available
        7. **Class/Standard**: Extract the class or standard
        8. **School/Institution**: Extract the school or institution name
        9. **Academic Year**: Extract the academic year or examination period
        
        Please format your response as a structured JSON object with the following format:
        
        ```json
        {
            "rrn": "extracted_roll_number",
            "student_name": "extracted_student_name",
            "class": "extracted_class",
            "school": "extracted_school_name",
            "academic_year": "extracted_academic_year",
            "sectionwise_marks": [
                {
                    "subject": "subject_name",
                    "marks_obtained": "marks",
                    "max_marks": "maximum_marks"
                }
            ],
            "total_marks": "total_marks_obtained",
            "total_max_marks": "total_maximum_marks",
            "percentage": "calculated_percentage",
            "grade": "grade_if_available",
            "additional_info": "any_other_relevant_information"
        }
        ```
        
        Important guidelines:
        - Extract information exactly as shown in the marksheet
        - If any field is not clearly visible or available, mark it as "Not Available"
        - For sectionwise marks, include all subjects visible in the marksheet
        - Calculate percentage if not explicitly mentioned: (total_obtained/total_maximum)*100
        - Be precise and double-check extracted numbers
        - Maintain the JSON format strictly
        """
        return prompt
    
    def analyze_marksheet(self, image_base64: str) -> Dict[str, Any]:
        """Send image to Perplexity API and get extracted information"""
        try:
            prompt = self.create_extraction_prompt()
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.1  # Low temperature for more consistent extractions
            }
            
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                extracted_text = result['choices'][0]['message']['content']
                return self.parse_extraction_result(extracted_text)
            else:
                raise ValueError("No response received from API")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Error analyzing marksheet: {str(e)}")
    
    def parse_extraction_result(self, extracted_text: str) -> Dict[str, Any]:
        """Parse the API response and extract JSON data"""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'```json\n(.*?)\n```', extracted_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # If no code block, try to find JSON-like content
                json_match = re.search(r'\{.*\}', extracted_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    raise ValueError("No JSON found in response")
            
            # Parse JSON
            parsed_data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['rrn', 'sectionwise_marks', 'total_marks']
            for field in required_fields:
                if field not in parsed_data:
                    parsed_data[field] = "Not Available"
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            # If JSON parsing fails, create a basic structure from text
            return {
                "rrn": "Extraction Failed",
                "student_name": "Not Available",
                "sectionwise_marks": [],
                "total_marks": "Not Available",
                "error": f"Failed to parse response: {str(e)}",
                "raw_response": extracted_text
            }
    
    def create_csv_data(self, extracted_data: Dict[str, Any]) -> pd.DataFrame:
        """Convert extracted data to CSV format"""
        try:
            # Create main student info row
            main_data = {
                'RRN': extracted_data.get('rrn', 'Not Available'),
                'Student_Name': extracted_data.get('student_name', 'Not Available'),
                'Class': extracted_data.get('class', 'Not Available'),
                'School': extracted_data.get('school', 'Not Available'),
                'Academic_Year': extracted_data.get('academic_year', 'Not Available'),
                'Total_Marks': extracted_data.get('total_marks', 'Not Available'),
                'Total_Max_Marks': extracted_data.get('total_max_marks', 'Not Available'),
                'Percentage': extracted_data.get('percentage', 'Not Available'),
                'Grade': extracted_data.get('grade', 'Not Available')
            }
            
            # Add section-wise marks as separate columns
            sectionwise_marks = extracted_data.get('sectionwise_marks', [])
            
            if isinstance(sectionwise_marks, list) and sectionwise_marks:
                for i, subject_data in enumerate(sectionwise_marks):
                    if isinstance(subject_data, dict):
                        subject_name = subject_data.get('subject', f'Subject_{i+1}')
                        marks_obtained = subject_data.get('marks_obtained', 'N/A')
                        max_marks = subject_data.get('max_marks', 'N/A')
                        
                        # Clean subject name for column
                        clean_subject_name = re.sub(r'[^\w\s]', '', subject_name).replace(' ', '_')
                        
                        main_data[f'{clean_subject_name}_Marks'] = marks_obtained
                        main_data[f'{clean_subject_name}_Max'] = max_marks
            
            # Create DataFrame
            df = pd.DataFrame([main_data])
            return df
            
        except Exception as e:
            # Create error DataFrame
            error_df = pd.DataFrame([{
                'RRN': 'Error',
                'Error_Message': str(e),
                'Raw_Data': str(extracted_data)
            }])
            return error_df
    
    def save_to_csv(self, df: pd.DataFrame, filename: str = None) -> str:
        """Save DataFrame to CSV file"""
        try:
            if filename is None:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"marksheet_data_{timestamp}.csv"
            
            filepath = f"{Config.OUTPUT_DIR}/{filename}"
            df.to_csv(filepath, index=False)
            return filepath
            
        except Exception as e:
            raise Exception(f"Error saving CSV: {str(e)}")
    
    def process_marksheet(self, image_file) -> tuple[Dict[str, Any], pd.DataFrame, str]:
        """Main method to process marksheet image and return all results"""
        try:
            # Step 1: Encode image to base64
            image_base64 = self.encode_image_to_base64(image_file)
            
            # Step 2: Analyze marksheet using AI
            extracted_data = self.analyze_marksheet(image_base64)
            
            # Step 3: Create CSV data
            df = self.create_csv_data(extracted_data)
            
            # Step 4: Save to CSV
            csv_filepath = self.save_to_csv(df)
            
            return extracted_data, df, csv_filepath
            
        except Exception as e:
            raise Exception(f"Error processing marksheet: {str(e)}")