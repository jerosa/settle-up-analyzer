# Settle Up Analyzer

A comprehensive tool for analyzing and visualizing Settle Up expense data. This project includes both a command-line interface (CLI) for data processing and a web application for interactive analysis.

## Features

### CLI Tool
- Process Settle Up CSV exports
- Generate expense analysis by user
- Create visualization plots
- Export processed data in Excel or CSV format
- Automatic latest file detection
- Configurable output formats and directories

### Web Application
- Interactive expense analysis dashboard
- Category-wise expense breakdown
- Monthly expense trends
- Expense predictions
- User-friendly interface with responsive design
- Real-time data visualization

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- virtualenv or venv (recommended)

### Basic Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/settle-up-analyzer.git
cd settle-up-analyzer
```

2. Create and activate a virtual environment:
```bash
# Linux/macOS
python -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### Installation Options

You have several options depending on your needs:

#### Option 1: Direct Use (No Installation)
Install only the required dependencies:
```bash
# For web application
pip install -r requirements.txt

# For development (includes all dependencies)
pip install -r requirements-dev.txt
```

#### Option 2: Package Installation
Install the package with specific components:
```bash
# Install core functionality only
pip install -e .

# Install with CLI support
pip install -e .[cli]

# Install with web support
pip install -e .[web]

# Install everything
pip install -e .[all]
```

## Usage

The project includes a Makefile for common operations. View available commands with:
```bash
make help
```

### Web Application

You have several options to run the web application:

1. Using make (recommended):
```bash
# Install web dependencies
make install-web

# Run the application
make run-web
```

2. Using the convenience script:
```bash
python scripts/run_webapp.py
```

3. Using Flask directly:
```bash
export FLASK_APP=settle_up.web.app
export FLASK_ENV=development
flask run
```

The application will be available at `http://localhost:5000`

### CLI Tool

You have several options to use the CLI:

1. Using make (recommended):
```bash
# Install CLI dependencies
make install-cli

# Run the CLI with arguments
make run-cli args="process /path/to/data -u John"
```

2. Using the convenience script:
```bash
python scripts/run_cli.py process /path/to/data -u "John"
```

3. Using Python module directly:
```bash
python -m settle_up.cli.main process /path/to/data -u "John"
```

Common CLI options:
```bash
# Process specific file with CSV output
make run-cli args="process /path/to/data -u John -f march_transactions.csv -o csv"

# Process without visualizations
make run-cli args="process /path/to/data -u John --no-visualize"

# Process with custom output directory
make run-cli args="process /path/to/data -u John --output-dir /path/to/output"
```

## Development

### Quick Start

1. Setup development environment:
```bash
make dev-setup
```

2. Run quality checks:
```bash
make check
```

3. Run tests:
```bash
make test
# or with coverage
make test-cov
```

### Project Structure
```
settle-up-analyzer/
├── settle_up/
│   ├── cli/                 # CLI implementation
│   │   ├── commands/       # CLI command modules
│   │   └── main.py        # CLI entry point
│   ├── core/               # Core business logic
│   │   └── processor.py   # Data processing
│   ├── web/                # Web application
│   │   ├── static/        # Static assets
│   │   ├── templates/     # HTML templates
│   │   └── routes.py      # Web routes
│   └── utils/              # Shared utilities
├── tests/                  # Test suite
├── docs/                   # Documentation
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
└── setup.py               # Package configuration
```

### Development Installation

Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=settle_up

# Run specific test file
pytest tests/test_processor.py
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Run linting
make lint

# Run type checking
make typecheck

# Format code
make format

# Run all quality checks
make check
```

### Making Changes

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and ensure all tests pass:
```bash
make test
```

3. Submit a pull request with your changes

## Configuration

### Environment Variables

The application uses environment variables for configuration. You can set these in two ways:

1. Create a `.env` file in the project root (recommended):
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit the file with your settings
   nano .env
   ```

2. Set environment variables directly:
   ```bash
   export FLASK_DEBUG=1
   export FLASK_APP=settle_up.web.app
   ```

### Available Configuration Options

#### Web Application
| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_APP` | Flask application module | `settle_up.web.app` |
| `FLASK_DEBUG` | Enable debug mode | `1` |
| `FLASK_RUN_HOST` | Host to bind to | `0.0.0.0` |
| `FLASK_RUN_PORT` | Port to listen on | `5000` |
| `DATABASE_URL` | Database connection URL | `sqlite:///settle_up.db` |
| `SETTLE_UP_WORKDIR` | Default working directory | `./data` |

### Running the Application

You can override any configuration when running the application:

```bash
# Using make
FLASK_PORT=8000 FLASK_DEBUG=0 make run-web

# Using Flask directly
FLASK_PORT=8000 FLASK_DEBUG=0 flask run

# Using the convenience script
FLASK_PORT=8000 FLASK_DEBUG=0 python scripts/run_webapp.py
```
