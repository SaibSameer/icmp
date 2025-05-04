import os
import shutil
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 9):
        print("Python 3.9 or higher is required")
        sys.exit(1)

def install_requirements():
    """Install required Python packages."""
    print("\n📦 Installing Python requirements...")
    requirements_files = ['requirements.txt', 'backend/requirements.txt']
    for req_file in requirements_files:
        if os.path.exists(req_file):
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', req_file])

def setup_directories():
    """Create necessary directories."""
    print("\n📁 Setting up directories...")
    directories = ['logs', 'uploads', 'temp']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print("✅ Directories created successfully")

def prepare_env_file():
    """Check if .env file exists and is properly configured."""
    print("\n🔧 Checking environment configuration...")
    required_vars = [
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD',
        'DB_HOST',
        'DB_PORT',
        'DATABASE_URL'
    ]
    
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        return False
    
    with open('.env', 'r') as f:
        env_content = f.read()
    
    missing_vars = []
    for var in required_vars:
        if var not in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing environment variables:", ', '.join(missing_vars))
        return False
    
    print("✅ Environment configuration verified")
    return True

def setup_database():
    """Set up the database using setup_database.py."""
    print("\n🗄️ Setting up database...")
    try:
        import setup_database
        setup_database.setup_database()
        print("✅ Database setup completed")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {str(e)}")
        return False

def prepare_render_files():
    """Prepare files for Render deployment."""
    print("\n📤 Preparing files for upload...")
    
    # Create a temporary directory for the upload package
    temp_dir = Path('temp/render_upload')
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Files and directories to include
    include_items = [
        'backend/',
        'requirements.txt',
        'application.py',
        'build.sh',
        'render.yaml',
        'database_setup.sql',
        'setup_database.py',
        '.env'
    ]
    
    # Copy files to temp directory
    for item in include_items:
        src = Path(item)
        dst = temp_dir / src.name
        
        if src.is_file():
            shutil.copy2(src, dst)
        elif src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
    
    # Create zip file
    shutil.make_archive('render_upload', 'zip', temp_dir)
    
    # Cleanup
    shutil.rmtree(temp_dir)
    
    print("✅ Files prepared successfully")
    print("📦 Upload package created: render_upload.zip")

def main():
    """Main installation process."""
    print("🚀 Starting installation process...")
    
    # Check Python version
    check_python_version()
    
    # Install requirements
    install_requirements()
    
    # Setup directories
    setup_directories()
    
    # Check environment configuration
    if not prepare_env_file():
        print("\n❌ Installation failed: Environment configuration issues")
        return
    
    # Setup database
    if not setup_database():
        print("\n❌ Installation failed: Database setup issues")
        return
    
    # Prepare files for upload
    prepare_render_files()
    
    print("\n✨ Installation completed successfully!")
    print("\nNext steps:")
    print("1. Find the 'render_upload.zip' file in your current directory")
    print("2. Go to render.com and create a new Web Service")
    print("3. Upload the zip file when prompted")
    print("4. Configure the environment variables in the Render dashboard")
    print("5. Deploy your application")

if __name__ == "__main__":
    main()