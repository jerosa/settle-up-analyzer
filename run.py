"""Entry point for the FinAnalyzer application."""
from settle_up.web.app import app

if __name__ == "__main__":
    app.run_server(debug=True) 
