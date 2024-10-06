
# SquareAPI

## Overview

**SquareAPI** is a Django-based application designed to ease community trash collection. 



## Installation

### Prerequisites

Ensure you have the following installed:

- [Python](https://www.python.org/downloads/) (>=3.8)
- [pip](https://pip.pypa.io/en/stable/) (Python package installer)
- [virtualenv](https://virtualenv.pypa.io/en/latest/) (for creating isolated Python environments)

### Setting Up the Environment

1. **Clone the repository:**

   ```sh
   git clone https://github.com/philiptitus/squareapi.git
   cd squareapi

    Create and activate a virtual environment:

    sh

python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`

Install the required packages:

sh

pip install -r requirements.txt

Apply migrations:

sh

python manage.py migrate

Create a superuser (admin):

sh

python manage.py createsuperuser

Run the development server:

sh

    python manage.py runserver

    The application will be available at http://127.0.0.1:8000/.

Configuration

Update your configuration files if necessary:

    .env: Add your environment-specific variables in the .env file.

    Example:

    makefile

    SECRET_KEY=your-secret-key
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1

    settings.py: Ensure you configure the database settings and other environment-specific settings.

Running Tests

To run tests, use:

sh

python manage.py test

Deployment

For deployment instructions, refer to the Deployment section of the documentation.
Contributing

    Fork the repository.
    Create a new branch (git checkout -b feature/YourFeature).
    Commit your changes (git commit -am 'Add new feature').
    Push to the branch (git push origin feature/YourFeature).
    Create a new Pull Request.

License

This project is licensed under the MIT License - see the LICENSE file for details.
Contact

For any questions or issues, please contact me.

SquareAPI © [2024] by [Philip Titus].
Released under the MIT License.
