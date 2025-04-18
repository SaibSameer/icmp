# ICMP Events API

## Installation Guide

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)
- PostgreSQL database (provided by Render)

### Quick Installation

1. Clone or download this repository to your local machine

2. Make sure your `.env` file is properly configured with your Render database credentials:
   ```
   DB_NAME=icmp_db
   DB_USER=saik_taimeh
   DB_HOST=dpg-d0169m2l19vc739rdtv0-a
   DB_PORT=5432
   DB_PASSWORD=your_password
   DATABASE_URL=your_database_url
   ```

3. Run the installation script:
   ```bash
   python install.py
   ```

   This script will:
   - Check Python version compatibility
   - Install required dependencies
   - Set up necessary directories
   - Verify environment configuration
   - Set up the database tables
   - Prepare files for Render deployment

4. After successful installation, you'll find `render_upload.zip` in your current directory

### Deploying to Render

1. Go to [render.com](https://render.com) and sign in
2. Create a new Web Service
3. Choose "Upload Files" option
4. Upload the `render_upload.zip` file
5. Configure your service:
   - Name: `icmp-events-api` (or your preferred name)
   - Environment: `Python`
   - Build Command: `chmod +x build.sh && ./build.sh`
   - Start Command: `gunicorn application:application`

6. Add your environment variables in the Render dashboard (they should match your `.env` file)

7. Deploy your application

### Verifying the Installation

To verify that everything is working:

1. Check the deployment logs in Render dashboard
2. Test the API endpoints:
   - Health check: `https://your-app-url/health`
   - API base: `https://your-app-url/api`

### Troubleshooting

If you encounter any issues:

1. Check the logs in the Render dashboard
2. Verify your environment variables are correctly set
3. Ensure the database is accessible
4. Check the application logs in the `/logs` directory

### Support

If you need help, please:
1. Check the error messages and logs
2. Review the documentation
3. Contact the development team

## License

[Your License Information] 