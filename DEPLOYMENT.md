# Deploying to Render

This document provides instructions for deploying the ICMP Events API to Render.

## Prerequisites

- A Render account (sign up at [render.com](https://render.com))
- A PostgreSQL database (you can use Render's PostgreSQL service)
- Your API keys and environment variables

## Deployment Steps

### 1. Set up a PostgreSQL Database on Render

1. Log in to your Render account
2. Click "New" and select "PostgreSQL"
3. Configure your database:
   - Name: `icmp_db` (or your preferred name)
   - PostgreSQL Version: 14 (or latest)
   - Database: `icmp_db`
   - Username: `icmp_user` (or your preferred username)
   - Password: Generate a secure password
4. Click "Create Database"
5. Note down the connection details (especially the `DATABASE_URL`)

### 2. Deploy the Web Service

1. Log in to your Render account
2. Click "New" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - Name: `icmp-events-api` (or your preferred name)
   - Environment: `Python`
   - Build Command: `chmod +x build.sh && ./build.sh`
   - Start Command: `gunicorn application:application`
   - Plan: Choose based on your needs (Free tier is good for testing)

### 3. Configure Environment Variables

Add the following environment variables in the Render dashboard:

- `DB_NAME`: Your database name (e.g., `icmp_db`)
- `DB_USER`: Your database username (e.g., `icmp_user`)
- `DB_PASSWORD`: Your database password
- `DB_HOST`: Your database host (from Render)
- `DB_PORT`: Your database port (usually `5432`)
- `DATABASE_URL`: The full connection URL from Render
- `OPENAI_API_KEY`: Your OpenAI API key
- `ICMP_API_KEY`: Your ICMP API key
- `REACT_APP_API_KEY`: Your React app API key

### 4. Deploy

1. Click "Create Web Service"
2. Render will automatically deploy your application
3. Once deployed, you can access your API at the URL provided by Render

## Troubleshooting

If you encounter issues during deployment:

1. Check the build logs in the Render dashboard
2. Verify that all environment variables are set correctly
3. Ensure your database is accessible from the web service
4. Check that your application is listening on the port specified by Render (usually port 10000)

## Updating Your Deployment

To update your deployment:

1. Push changes to your GitHub repository
2. Render will automatically detect the changes and redeploy your application

## Monitoring

You can monitor your application's performance and logs in the Render dashboard:

1. Go to your web service in the Render dashboard
2. Click on "Logs" to view application logs
3. Click on "Metrics" to view performance metrics 