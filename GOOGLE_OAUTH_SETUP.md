# Google OAuth Setup Guide

## 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name: "Aiza's Fine Art"
4. Click "Create"

## 2. Enable Google+ API

1. In the left sidebar, go to "APIs & Services" → "Library"
2. Search for "Google+ API"
3. Click on it and click "Enable"

## 3. Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" (for public use)
3. Fill in required fields:
   - App name: "Aiza's Fine Art"
   - User support email: your email
   - Developer contact: your email
4. Add scopes:
   - `../auth/userinfo.email`
   - `../auth/userinfo.profile`
5. Add test users (your email addresses)

## 4. Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Application type: "Web application"
4. Name: "Aiza's Fine Art Web Client"
5. Authorized JavaScript origins:
   - `http://localhost:8001`
   - `http://127.0.0.1:8001`
   - `https://yourdomain.com` (for production)
6. Authorized redirect URIs:
   - `http://localhost:8001/accounts/google/login/callback/`
   - `http://127.0.0.1:8001/accounts/google/login/callback/`
   - `https://yourdomain.com/accounts/google/login/callback/` (for production)

## 5. Add Credentials to Django

1. Copy the Client ID and Client Secret
2. Add them to your `.env` file:
   ```
   GOOGLE_OAUTH2_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
   GOOGLE_OAUTH2_CLIENT_SECRET=your-client-secret-here
   ```

## 6. Configure in Django Admin

1. Start your Django server: `python manage.py runserver 8001`
2. Go to `http://localhost:8001/admin/`
3. Login with: Username: `Aiza`, Password: `Aiza@rt12345`
4. Go to "Sites" → "Sites"
5. Click on "example.com" and change:
   - Domain name: `localhost:8001`
   - Display name: `Aiza's Fine Art`
6. Go to "Social Applications" → "Add Social Application"
7. Fill in:
   - Provider: Google
   - Name: Google OAuth
   - Client id: (your Google client ID)
   - Secret key: (your Google client secret)
   - Sites: Select "localhost:8001"

## 7. Test OAuth

1. Go to `http://localhost:8001/accounts/login/`
2. Click "Continue with Google"
3. You should be redirected to Google's OAuth flow

## Security Notes

- Never commit your `.env` file with real credentials
- Use different credentials for development and production
- Regularly rotate your OAuth secrets
- Monitor OAuth usage in Google Cloud Console

## Production Setup

For production deployment:

1. Update authorized origins and redirect URIs in Google Cloud Console
2. Update `CSRF_TRUSTED_ORIGINS` in settings
3. Set `SECURE_SSL_REDIRECT=True` for HTTPS
4. Update Site domain in Django admin to your production domain