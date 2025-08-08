<<<<<<< HEAD
# porfolio
=======
# Portfolio Website

A professional portfolio website built with Django and modern frontend technologies.

## Features
- Responsive design
- Interactive project showcase
- Blog system
- Contact form with MongoDB integration
- Resume download functionality
- Social media integration

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```
SECRET_KEY=your_secret_key
MONGODB_URI=your_mongodb_uri
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

## Project Structure
- `portfolio/` - Main Django project
- `core/` - Core application
- `static/` - Static files (CSS, JS, images)
- `templates/` - HTML templates
- `media/` - User-uploaded files 
>>>>>>> 06ae244 (Initial commit)
