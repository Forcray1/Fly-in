NAME        = fly-in.py
VENV        = .venv
PYTHON      = $(VENV)/bin/python3
PIP         = $(VENV)/bin/pip
MAP         = maps/easy/01_linear_path.txt

GREEN       = \033[0;32m
RED         = \033[0;31m
RESET       = \033[0m

all: $(VENV)
	@echo "$(GREEN)Simulation ready.$(RESET)"

$(VENV): requirements.txt
	@echo "$(GREEN)Creating Virtual Environment...$(RESET)"
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run: all
	$(PYTHON) $(NAME) $(MAP)

debug: all
	$(PYTHON) -m pdb $(NAME) $(MAP)

lint: all
	@echo "$(GREEN)Running Flake8 and Mypy...$(RESET)"
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --ignore-missing-imports --disallow-untyped-defs

clean:
	@echo "$(RED)Cleaning python caches...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete

fclean: clean
	@echo "$(RED)Removing virtual environment...$(RESET)"
	rm -rf $(VENV)
	rm -f uv.lock
	rm -f data/output/function_calling_results.json

re: fclean all

.PHONY: all run debug clean fclean lint re