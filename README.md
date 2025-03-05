# Settle Up Analyzer

A web application for analyzing Settle Up expenses data.

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

To run the application:

```bash
python run.py
```

The application will be available at http://localhost:8050

## Project Structure

```
settle_up/
├── core/           # Core business logic
├── web/            # Web application
│   ├── pages/      # Dash pages
│   ├── static/     # Static files
│   └── templates/  # Templates
├── tests/          # Test files
└── docs/           # Documentation
```

## Development

- The application uses Dash for the web interface
- Pages are modular and located in `settle_up/web/pages/`
- Core business logic is separated in the `settle_up/core/` package
