# Flask Application API with Python Selenium

This project is a Flask-based web application that integrates Python Selenium for automated browser testing. It provides APIs for interacting with web pages and performing automated tasks.

## Features
- **Flask Framework**: Simplifies API development.
- **Python Selenium**: Enables browser automation.
- **Modular Design**: Ensures scalability and maintainability.

## Prerequisites
Ensure the following are installed:
- **Python**: Version 3.8 or higher.
- **pip**: Python's package manager.
- **Google Chrome**: Latest version recommended.
- **ChromeDriver**: Compatible with your Chrome version.

## Installation
1. **Clone the Repository**:
    ```bash
    git clone https://github.com/Obaidul-007/flask_application_api_python_selenium
    cd flask_application_api_python_selenium
    ```

2. **Set Up Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application
1. **Start the Flask Server**:
    ```bash
    python app.py
    ```

2. **Access the Application**:
   Visit `http://127.0.0.1:5000` in your browser.

## Running Tests
1. **Start the Flask Server** (if not already running).
2. **Run Tests**:
    ```bash
    python -m unittest discover tests
    ```

## Project Structure
```
flask_application_api_python_selenium/
├── app.py                # Main Flask application
├── tests/                # Unit tests
├── requirements.txt      # Project dependencies
├── README.md             # Project documentation
└── ...                   # Other files and directories
```

## Contributing
Contributions are encouraged! Fork the repository, make your changes, and submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

