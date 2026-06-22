.PHONY: test results notebook reproduce paper

test:
	python -m unittest discover -s tests -v

results:
	python -m context_games.reproduce --output-dir results

notebook:
	python scripts/build_notebook.py

reproduce:
	python scripts/run_all.py

paper:
	cd manuscript && latexmk -pdf -interaction=nonstopmode -halt-on-error context_dependent_benefit_loss_games_v09.tex
