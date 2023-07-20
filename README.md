# Django REST Token Authentication Boilerplate

This repository provides a reusable implementation of token-based authentication using Django REST Framework. The included features are user registration, login, password change, and profile retrieval.

## Overview
This boilerplate project uses:
- Django and Django REST Framework for the backend.
- Knox for token-based authentication.

The project exposes the following endpoints:
- User Registration: `/api/auth/register/`
- User Login: `/api/auth/login/`
- Change Password: `/api/auth/change-password/`
- Profile Retrieval: `/api/auth/profile/`
- Logout: `/api/auth/logout/`
- Logout All Sessions: `/api/auth/logoutall/`

## Getting Started

To use this boilerplate, follow these steps:

1. Clone this repository and navigate to the project directory.
2. Set up a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Make migrations and migrate:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Run the Django server:
   ```
   python manage.py runserver
   ```
6. You can now use the authentication endpoints on `localhost:8000/api/auth/`.

## Endpoints

- **User Registration** `/api/auth/register/`: 
  - Request type: POST
  - Request body should include `username`, `email`, and `password`

- **User Login** `/api/auth/login/`: 
  - Request type: POST
  - Request body should include `username` and `password`
  - On successful login, a token will be returned which should be used for authenticated requests

- **Change Password** `/api/auth/change-password/`:
  - Request type: PUT
  - Request body should include `old_password` and `new_password`
  - Requires authentication

- **Profile Retrieval** `/api/auth/profile/`:
  - Request type: GET
  - Requires authentication

- **Logout** `/api/auth/logout/`:
  - Request type: POST
  - Requires authentication

- **Logout All Sessions** `/api/auth/logoutall/`:
  - Request type: POST
  - Requires authentication

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.