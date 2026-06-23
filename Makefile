.PHONY: test results notebook reproduce

test:
	python -m unittest discover -s tests -v

results:
	python -m context_games.reproduce --output-dir results

notebook:
	python scripts/build_notebook.py

reproduce:
	python scripts/run_all.py
