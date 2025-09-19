# Aiza's Fine Art - Professional Art Business Website

A modern, professional art business website built for Aiza, a watercolor and oil painter based in Fort Worth, TX. This platform combines Django backend with React components and Tailwind CSS for a modern, SEO-friendly art portfolio and e-commerce platform.

## 🎨 Features

### Core Functionality
- **Professional Art Portfolio**: Showcase watercolor and oil paintings with high-quality image display
- **E-commerce Integration**: Sell original artworks with Stripe payment processing
- **Print Fulfillment**: Lumaprints integration for print orders and fulfillment
- **Custom Commissions**: Inquiry system for custom artwork requests
- **User Accounts**: Social login, wishlist, order tracking, and preferences
- **Blog System**: Artist insights, process documentation, and news
- **Newsletter**: Email marketing and customer engagement

### Technical Highlights
- **Hybrid Architecture**: Django templates for SEO with React components for interactivity
- **Modern Styling**: Tailwind CSS with custom art-focused design system
- **Cloud Storage**: Supabase for database and image storage with CDN
- **Responsive Design**: Mobile-first approach optimized for art browsing
- **SEO Optimized**: Server-side rendering with dynamic meta tags
- **Performance**: Image optimization, lazy loading, and caching strategies

## 🛠 Tech Stack

### Backend
- **Django 4.2+** with Django REST Framework
- **Supabase PostgreSQL** for database
- **Supabase Storage** for file storage and CDN
- **Celery + Redis** for background tasks
- **Django Allauth** for authentication

### Frontend
- **Django Templates** for SEO-critical pages
- **React 18** for interactive components
- **Tailwind CSS** for styling
- **Webpack** for asset bundling

### Integrations
- **Stripe** for payment processing
- **Lumaprints** for print fulfillment
- **SendGrid** for email notifications
- **Twilio** for SMS notifications
- **Firebase Cloud Messaging** for push notifications

### Hosting & Deployment
- **Fly.io** for application hosting
- **Supabase** for database and storage
- **Docker** for containerization

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (or Supabase account)
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd AizasFineArt
```

### 2. Set Up Python Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set Up Node.js Dependencies
```bash
npm install
```

### 4. Environment Configuration
Copy `.env.example` to `.env` and configure your settings:

```bash
cp .env.example .env
```

Required environment variables:
- `SUPABASE_URL` and `SUPABASE_KEY` (from Supabase dashboard)
- `DATABASE_URL` (Supabase PostgreSQL connection string)
- `SECRET_KEY` (Django secret key)
- `STRIPE_PUBLISHABLE_KEY` and `STRIPE_SECRET_KEY`
- Email and SMS service credentials

### 5. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Build Assets
```bash
npm run build
```

### 7. Run Development Server
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

For development with auto-reloading CSS:
```bash
npm run dev  # In a separate terminal
```

## 📁 Project Structure

```
AizasFineArt/
├── aizasfineart/           # Django project settings
├── apps/                   # Django applications
│   ├── core/              # Core pages and utilities
│   ├── artwork/           # Artwork models and views
│   ├── users/             # User management
│   ├── orders/            # E-commerce and orders
│   ├── blog/              # Blog and content
│   └── notifications/     # Notification system
├── templates/             # Django templates
│   ├── base.html         # Base template
│   └── core/             # Core page templates
├── static/               # Static assets
│   ├── src/              # Source files
│   │   ├── input.css     # Tailwind CSS input
│   │   └── js/           # JavaScript/React components
│   └── dist/             # Built assets
├── utils/                # Utility functions
│   └── supabase_client.py # Supabase integration
├── requirements.txt      # Python dependencies
├── package.json         # Node.js dependencies
├── tailwind.config.js   # Tailwind configuration
├── webpack.config.js    # Webpack configuration
└── Dockerfile          # Docker configuration
```

## 🎯 Development Guide

### Adding New Artworks
1. Access Django admin at `/admin/`
2. Navigate to Artwork section
3. Add new artwork with details and upload image
4. Images are automatically optimized and uploaded to Supabase

### Customizing Styles
- Modify `static/src/input.css` for custom styles
- Update `tailwind.config.js` for theme customization
- Run `npm run build:css` to rebuild styles

### Creating React Components
- Add components to `static/src/js/components/`
- Import and use in Django templates
- Build with `npm run build:js`

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## 🔧 Configuration

### Supabase Setup
1. Create a new Supabase project
2. Set up the database schema using Django migrations
3. Create a storage bucket named `artwork-images`
4. Configure RLS policies for public read access

### Stripe Configuration
1. Create Stripe account and get API keys
2. Set up webhook endpoints for payment processing
3. Configure product catalog for print options

### Email Configuration
1. Set up SendGrid account
2. Create email templates for notifications
3. Configure SMTP settings in Django

## 📈 Performance Optimization

### Image Optimization
- Images are automatically resized and optimized on upload
- Multiple variants generated for different use cases
- CDN delivery through Supabase Storage
- Lazy loading implemented for improved performance

### Caching Strategy
- Django template caching for static content
- Redis caching for database queries
- Browser caching for static assets
- CDN caching for images

### SEO Optimization
- Server-side rendering for all public pages
- Dynamic meta tags and Open Graph data
- Structured data markup for artwork
- XML sitemaps with image sitemaps

## 🚀 Deployment

### Fly.io Deployment
```bash
fly launch
fly deploy
```

### Environment Variables
Set production environment variables:
```bash
fly secrets set SECRET_KEY=your-secret-key
fly secrets set DATABASE_URL=your-database-url
# ... other secrets
```

### Database Migration
```bash
fly ssh console
python manage.py migrate
python manage.py createsuperuser
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is proprietary software developed for Aiza's Fine Art business.

## 📞 Support

For support or questions about this project, please contact the development team.

---

**Built with ❤️ for Aiza's Fine Art in Fort Worth, TX**