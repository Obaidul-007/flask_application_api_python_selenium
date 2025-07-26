# Test Automation Makefile

.PHONY: help install test smoke regression api ui staging production parallel clean reports setup

help:
	@echo "Test Automation Framework Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  setup       - Complete project setup"
	@echo "  install     - Install Python dependencies"
	@echo ""
	@echo "Test Execution:"
	@echo "  test        - Run all tests"
	@echo "  smoke       - Run smoke tests (critical functionality)"
	@echo "  regression  - Run regression tests (comprehensive)"
	@echo "  api         - Run API tests only"
	@echo "  ui          - Run UI tests only"
	@echo "  integration - Run integration tests"
	@echo ""
	@echo "Environment-Specific:"
	@echo "  staging     - Run staging environment tests"
	@echo "  production  - Run production environment tests"
	@echo ""
	@echo "Advanced:"
	@echo "  parallel    - Run tests in parallel"
	@echo "  debug       - Run tests with debug output"
	@echo "  headless    - Run tests in headless mode"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean       - Clean reports and logs"
	@echo "  reports     - Generate and open test reports"
	@echo "  check       - Check framework health"

setup:
	@echo "🔧 Setting up Test Automation Framework..."
	python -m venv venv || echo "Virtual environment already exists"
	@echo " Installing dependencies..."
	pip install -r requirements.txt
	@echo "📁 Creating directory structure..."
	mkdir -p reports/{html,json,screenshots,logs}
	mkdir -p test_data
	@echo " Setup complete!"

install:
	@echo " Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo " Dependencies installed!"

test:
	@echo " Running all tests..."
	pytest --env=local --browser=chrome

smoke:
	@echo " Running smoke tests..."
	pytest -m smoke --env=local --browser=chrome

regression:
	@echo "🔄 Running regression tests..."
	pytest -m regression --env=local --browser=chrome

api:
	@echo " Running API tests..."
	pytest -m api --env=local

ui:
	@echo " Running UI tests..."
	pytest -m ui --env=local --browser=chrome

integration:
	@echo "🔗 Running integration tests..."
	pytest -m integration --env=local --browser=chrome

staging:
	@echo "🏗️  Running staging tests..."
	pytest -m staging --env=staging --browser=headless

production:
	@echo "🏭 Running production tests..."
	pytest -m production --env=production --browser=headless

parallel:
	@echo "⚡ Running tests in parallel..."
	pytest -n auto --env=local --browser=chrome

debug:
	@echo "🔍 Running tests with debug output..."
	pytest --log-cli-level=DEBUG -v -s --env=local --browser=chrome

headless:
	@echo " Running tests in headless mode..."
	pytest --env=local --browser=headless

clean:
	@echo "🧹 Cleaning up..."
	rm -rf reports/html/* reports/json/* reports/screenshots/* reports/logs/*
	rm -rf .pytest_cache/ __pycache__/ */__pycache__/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	@echo "✅ Cleanup complete!"

reports:
	@echo "📊 Opening test reports..."
	@if [ -f "reports/html/report.html" ]; then \
		echo "Opening HTML report..."; \
		python -m webbrowser reports/html/report.html; \
	else \
		echo "❌ No HTML report found. Run tests first."; \
	fi

check:
	@echo "🏥 Checking framework health..."
	@echo "Python version: $$(python --version)"
	@echo "Pip packages:"
	@pip list | grep -E "(pytest|selenium|flask|faker)"
	@echo "Project structure:"
	@find . -name "*.py" -type f | head -10
	@echo "✅ Health check complete!"

# Development helpers
dev-server:
	@echo "🖥️  Starting development server..."
	python app.py

kill-server:
	@echo "🔪 Stopping any running Flask servers..."
	@pkill -f "python app.py" || echo "No Flask servers running"

fresh-start: clean kill-server dev-server
