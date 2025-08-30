# Notion ICS Calendar Feed Server - Makefile

# Variables
PYTHON = python3
VENV = venv
APP_MODULE = app.main:app

# Setup targets
.PHONY: install setup run dev clean test

# Install dependencies
install:
	$(PYTHON) -m pip install -r requirements.txt

# Setup development environment
setup:
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && pip install -r requirements.txt
	cp .env.example .env
	@echo "Setup complete! Edit .env with your Notion token"

# Run in production mode
run:
	$(PYTHON) -m uvicorn $(APP_MODULE) --host 0.0.0.0 --port 8000

# Run in development mode with auto-reload
dev:
	$(PYTHON) -m uvicorn $(APP_MODULE) --reload --host 0.0.0.0 --port 8000

# Run using the convenience script
run-script:
	$(PYTHON) run_server.py

# Run example
example:
	$(PYTHON) example.py

# Clean up
clean:
	rm -rf __pycache__
	rm -rf app/__pycache__
	rm -rf $(VENV)
	rm -f example_calendar.ics

# Show help
help:
	@echo "Available targets:"
	@echo "  install     - Install Python dependencies"
	@echo "  setup       - Set up development environment"
	@echo "  run         - Run server in production mode"
	@echo "  dev         - Run server in development mode"
	@echo "  run-script  - Run using convenience script"
	@echo "  example     - Run example usage script"
	@echo "  clean       - Clean up generated files"
	@echo "  help        - Show this help message"
