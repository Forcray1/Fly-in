install:
    python3 -m venv .venv
	.venv\Scripts\activate && pip install --upgrade pip && pip install -r requirements.txt

run:
    python3 fly-in.py maps/medium/01_dead_end_trap.txt

debug:
    python3 -m pdb fly-in.py maps/medium/01_dead_end_trap.txt

clean:
    rmdir /S /Q $(VENV_DIR) 2>NUL || exit 0
    for /d /r %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
    del /s /q *.pyc *.pyo 2>NUL || exit 0
    del /s /q *~ 2>NUL || exit 0
    del /s /q uv.lock 2>NUL || exit 0
    del /s /q data\output\function_calling_results.json 2>NUL || exit 0

lint:
    python3 -m flake8
    python3 -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
    python3 -m flake8
    python3 -m mypy . --strict

.PHONY: install run debug clean lint lint-strict