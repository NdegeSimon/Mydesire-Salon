# My Desire Salon Application

A complete salon booking application with user authentication, appointment scheduling, and management features.

## Features

- User registration and login
- Salon attendant profiles
- Appointment booking system
- Profile management
- Gallery showcase

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone or download the repository
2. Navigate to the project directory
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

### Method 1: Using the startup script (Recommended)

```bash
python start_app.py
```

This will:
- Initialize the database
- Add sample data (attendants and a test user)
- Start the FastAPI backend server on http://localhost:8000

### Method 2: Manual start

1. Start the backend server:
```bash
uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

2. Open the frontend by opening `index.html` in your browser

## Default User Credentials

- Email: alice@example.com
- Password: password123

## API Endpoints

- **Base URL**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs

## File Structure

```
My-Desire-Salon/
├── backend/          # Backend API and database models
├── images/           # Image assets
├── index.html        # Home page
├── login.html        # Login page
├── Signup.html       # Registration page
├── book.html         # Appointment booking page
├── profile.html      # User profile page
├── gallery.html      # Gallery page
├── requirements.txt  # Python dependencies
├── start_app.py      # Application startup script
└── README.md         # This file
```

## Development

To modify the application:

1. Backend code is in the `backend/` directory
2. Frontend HTML files are in the root directory
3. Styles are defined in each HTML file

## Troubleshooting

If you encounter any issues:

1. Make sure all dependencies are installed
2. Check that port 8000 is not being used by another application
3. Ensure the database file (users.db) has proper read/write permissions

## License

Copyright (c) 2025 Petley Inc. All rights reserved.
Unauthorized copying, modification, or distribution of this software is prohibited.