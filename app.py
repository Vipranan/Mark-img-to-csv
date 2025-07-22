"""
Streamlit Frontend for Marksheet AI Agent
"""
import streamlit as st
import pandas as pd
from PIL import Image
import io
import traceback
from marksheet_agent import MarksheetAgent
from config import Config

# Page configuration
st.set_page_config(
    page_title="Marksheet AI Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    """Initialize session state variables"""
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'extracted_data' not in st.session_state:
        st.session_state.extracted_data = None
    if 'csv_data' not in st.session_state:
        st.session_state.csv_data = None
    if 'csv_filepath' not in st.session_state:
        st.session_state.csv_filepath = None

def validate_image(uploaded_file) -> bool:
    """Validate uploaded image file"""
    if uploaded_file is None:
        return False
    
    # Check file size
    if uploaded_file.size > Config.MAX_FILE_SIZE:
        st.error(f"File size too large. Maximum allowed size is {Config.MAX_FILE_SIZE / (1024*1024):.1f} MB")
        return False
    
    # Check file extension
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension not in Config.ALLOWED_EXTENSIONS:
        st.error(f"Unsupported file format. Allowed formats: {', '.join(Config.ALLOWED_EXTENSIONS)}")
        return False
    
    return True

def display_extracted_data(data):
    """Display extracted data in a formatted way"""
    st.subheader("📋 Extracted Information")
    
    # Basic Information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Student Information:**")
        st.write(f"**RRN:** {data.get('rrn', 'Not Available')}")
        st.write(f"**Name:** {data.get('student_name', 'Not Available')}")
        st.write(f"**Class:** {data.get('class', 'Not Available')}")
        st.write(f"**School:** {data.get('school', 'Not Available')}")
    
    with col2:
        st.markdown("**Academic Information:**")
        st.write(f"**Academic Year:** {data.get('academic_year', 'Not Available')}")
        st.write(f"**Total Marks:** {data.get('total_marks', 'Not Available')}")
        st.write(f"**Maximum Marks:** {data.get('total_max_marks', 'Not Available')}")
        st.write(f"**Percentage:** {data.get('percentage', 'Not Available')}")
        if data.get('grade'):
            st.write(f"**Grade:** {data.get('grade')}")
    
    # Section-wise Marks
    st.markdown("**📚 Section-wise Marks:**")
    sectionwise_marks = data.get('sectionwise_marks', [])
    
    if sectionwise_marks and isinstance(sectionwise_marks, list):
        marks_df = pd.DataFrame(sectionwise_marks)
        if not marks_df.empty:
            st.dataframe(marks_df, use_container_width=True)
        else:
            st.info("No section-wise marks data available")
    else:
        st.info("No section-wise marks data available")

def display_csv_data(df):
    """Display CSV data"""
    st.subheader("📊 CSV Data Preview")
    st.dataframe(df, use_container_width=True)

def main():
    """Main Streamlit application"""
    init_session_state()
    
    # Header
    st.title("📊 Marksheet AI Agent")
    st.markdown("Upload a marksheet image to extract student information, marks, and generate CSV data.")
    
    # Sidebar
    with st.sidebar:
        st.header("ℹ️ Information")
        st.markdown("""
        **What this app does:**
        - Extracts RRN (Roll Number)
        - Extracts section-wise marks
        - Calculates total marks
        - Generates CSV output
        
        **Supported formats:**
        - PNG, JPG, JPEG, BMP, TIFF
        - Max file size: 10MB
        
        **Requirements:**
        - Clear, readable marksheet image
        - Good lighting and contrast
        - Minimal blur or distortion
        """)
        
        # Configuration status
        st.header("🔧 Configuration")
        try:
            Config.validate_config()
            st.success("✅ Configuration valid")
        except Exception as e:
            st.error(f"❌ Configuration error: {str(e)}")
            st.stop()
    
    # Main content
    # File upload section
    st.header("📁 Upload Marksheet")
    uploaded_file = st.file_uploader(
        "Choose a marksheet image",
        type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
        help="Upload a clear image of the marksheet"
    )
    
    if uploaded_file is not None:
        if validate_image(uploaded_file):
            # Display uploaded image
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("📷 Uploaded Image")
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Marksheet", use_column_width=True)
                
                # Reset file pointer
                uploaded_file.seek(0)
            
            with col2:
                st.subheader("🚀 Processing")
                
                if st.button("🔍 Extract Information", type="primary", use_container_width=True):
                    try:
                        # Show progress
                        with st.spinner("🤖 Analyzing marksheet with AI..."):
                            # Initialize agent
                            agent = MarksheetAgent()
                            
                            # Process marksheet
                            progress_bar = st.progress(0)
                            
                            progress_bar.progress(25)
                            st.write("📷 Encoding image...")
                            
                            progress_bar.progress(50)
                            st.write("🧠 Extracting information...")
                            
                            extracted_data, csv_data, csv_filepath = agent.process_marksheet(uploaded_file)
                            
                            progress_bar.progress(75)
                            st.write("📊 Generating CSV...")
                            
                            progress_bar.progress(100)
                            st.write("✅ Processing complete!")
                            
                            # Store in session state
                            st.session_state.processing_complete = True
                            st.session_state.extracted_data = extracted_data
                            st.session_state.csv_data = csv_data
                            st.session_state.csv_filepath = csv_filepath
                            
                            st.success("🎉 Information extracted successfully!")
                            
                    except Exception as e:
                        st.error(f"❌ Error processing marksheet: {str(e)}")
                        st.expander("🔍 Error Details").write(traceback.format_exc())
    
    # Display results if processing is complete
    if st.session_state.processing_complete:
        st.divider()
        
        # Display extracted data
        if st.session_state.extracted_data:
            display_extracted_data(st.session_state.extracted_data)
        
        st.divider()
        
        # Display CSV data
        if st.session_state.csv_data is not None:
            display_csv_data(st.session_state.csv_data)
            
            # Download button
            csv_string = st.session_state.csv_data.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv_string,
                file_name="marksheet_data.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )
        
        # Clear results button
        if st.button("🗑️ Clear Results", type="secondary"):
            st.session_state.processing_complete = False
            st.session_state.extracted_data = None
            st.session_state.csv_data = None
            st.session_state.csv_filepath = None
            st.rerun()
    
    # Footer
    st.divider()
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Built with ❤️ using Streamlit and Perplexity AI"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()