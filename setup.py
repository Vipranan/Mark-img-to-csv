import os
import subprocess
import sys

def run_command(command, cwd=None):
    result = subprocess.run(command, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ Command failed: {command}")
        sys.exit(1)

print("🚀 Starting Conda-Activated Project Setup...")

# Step 1: Install Python Backend Dependencies
print("📦 Installing Backend Python Dependencies into conda environment...")
if not os.path.exists("backend/requirements.txt"):
    os.makedirs("backend", exist_ok=True)
    with open("backend/requirements.txt", "w") as f:
        f.write("\n".join([
            "fastapi",
            "uvicorn",
            "python-multipart",
            "pytesseract",
            "opencv-python",
            "pillow",
            "python-dotenv"
        ]))

run_command("pip install -r backend/requirements.txt")

# Step 2: Frontend Setup with Vite + Tailwind
print("📂 Setting up Frontend (React + Tailwind)...")
if not os.path.exists("frontend"):
    os.makedirs("frontend")

if not os.path.exists("frontend/package.json"):
    print("Creating Vite React App...")
    run_command("npm create vite@latest frontend -- --template react")

print("Installing Frontend Dependencies...")
run_command("npm install", cwd="frontend")
run_command("npm install -D tailwindcss postcss autoprefixer", cwd="frontend")
run_command("npx tailwindcss init -p", cwd="frontend")

# Update Tailwind Config (simplified)
tailwind_config_path = "frontend/tailwind.config.js"
if os.path.exists(tailwind_config_path):
    with open(tailwind_config_path, "r") as file:
        content = file.read()
    content = content.replace("content: []", 'content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"]')
    with open(tailwind_config_path, "w") as file:
        file.write(content)

# Step 3: Generate .env Template
if not os.path.exists(".env"):
    print("Creating .env template...")
    with open(".env", "w") as env_file:
        env_file.write("GOOGLE_CLIENT_ID=\nGOOGLE_CLIENT_SECRET=\n")

# Step 4: Tesseract Reminder
print("\n⚠️ Please ensure Tesseract OCR is installed and added to PATH.")
print("Download link: https://github.com/UB-Mannheim/tesseract/wiki")

print("\n🎉 Setup Complete! 🚀")
print("To run backend: uvicorn backend.app.main:app --reload")
print("To run frontend: cd frontend && npm run dev")
