.PHONY: help clean clean_doc clean_pycache test run runi doc doc_html doc_pdf

# === Aux rules ==============================================================
# Help rules
help:
	@echo ' ================================================================== '
	@echo ' THIS MAKEFILE REQUIRES PIPENV                                      '
	@echo ' ================================================================== '
	@echo 'clean          : clean whole project(documentation, __pycache, ....)'
	@echo 'clean_doc      : clean documentation'
	@echo 'clean_doc_html : clean html documentation'
	@echo 'clean_doc_pdf  : clean pdf documentation'
	@echo 'clean_pycache  : clean __pycache__'
	@echo 'run            : run main.py'
	@echo 'runi           : run main.py in interactive mode'
	@echo 'doc            : generate documentation both in pdf and html'
	@echo 'doc_html       : generate html documentation'
	@echo 'doc_pdf        : generate html documentation'
	@echo 'test           : execute all tests'

# Clean rules
clean: clean_doc clean_pycache

clean_doc: clean_doc_html clean_doc_pdf

clean_doc_html:
	@rm -Rf docs/build/html

clean_doc_pdf:
	@rm -Rf docs/build/pdf

clean_pycache:
	@find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf


# === Normal rules ===========================================================
# Run rules
run:
	python -m progTiroc

runi:
	python -i -m progTiroc


# === Dev rules ==============================================================
# Documentation rules
.sphinx_prep:
	@cd docs; sphinx-apidoc -f -o source ../ai/;

doc: doc_html doc_pdf

doc_html:
	@echo ${@:4};
	@cd docs; $(MAKE) html;

doc_pdf:
	@cd docs; $(MAKE) pdf;

# Test rules
test:
	pytest --cov=ai --cov-branch
