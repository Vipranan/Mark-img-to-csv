"""
Setup script for Marksheet AI Agent
This script helps users set up the environment and dependencies
"""
import os
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    else:
        print(f"✅ Python version: {sys.version.split()[0]}")
        return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    directories = ["output", "temp"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_env_file():
    """Create .env file if it doesn't exist"""
    print("\n🔧 Setting up environment file...")
    
    if not os.path.exists('.env'):
        # Copy from example
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as example_file:
                content = example_file.read()
            
            with open('.env', 'w') as env_file:
                env_file.write(content)
            
            print("✅ Created .env file from example")
            print("⚠️  Please edit .env file and add your Perplexity API key")
        else:
            # Create basic .env file
            with open('.env', 'w') as env_file:
                env_file.write("PERPLEXITY_API_KEY=your_api_key_here\n")
            
            print("✅ Created .env file")
            print("⚠️  Please edit .env file and add your Perplexity API key")
    else:
        print("✅ .env file already exists")

def validate_setup():
    """Validate the setup"""
    print("\n🔍 Validating setup...")
    
    # Check if all files exist
    required_files = [
        'app.py', 'marksheet_agent.py', 'config.py', 
        'utils.py', 'requirements.txt', '.env'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
    
    # Check if .env has API key
    try:
        with open('.env', 'r') as env_file:
            content = env_file.read()
            if 'your_api_key_here' in content:
                print("⚠️  Please add your actual Perplexity API key to .env file")
            else:
                print("✅ API key configuration detected")
    except:
        print("❌ Error reading .env file")
        return False
    
    return True

def print_instructions():
    """Print final setup instructions"""
    print("\n" + "="*50)
    print("🎉 SETUP COMPLETE!")
    print("="*50)
    
    print("\n📋 Next Steps:")
    print("1. Get your Perplexity API key from: https://www.perplexity.ai/settings/api")
    print("2. Edit the .env file and replace 'your_api_key_here' with your actual API key")
    print("3. Run the application: streamlit run app.py")
    
    print("\n🚀 To start the application:")
    print("   streamlit run app.py")
    
    print("\n📚 Project Structure:")
    print("   ├── app.py              # Main Streamlit application")
    print("   ├── marksheet_agent.py  # AI agent for marksheet processing")
    print("   ├── config.py           # Configuration settings")
    print("   ├── utils.py            # Utility functions")
    print("   ├── requirements.txt    # Python dependencies")
    print("   ├── .env                # Environment variables")
    print("   └── output/             # Generated CSV files")

def main():
    """Main setup function"""
    print("🚀 Marksheet AI Agent Setup")
    print("="*30)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed during package installation")
        return
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Validate setup
    if validate_setup():
        print_instructions()
    else:
        print("❌ Setup validation failed")

if __name__ == "__main__":
    main()