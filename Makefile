.PHONY: help clean clean_doc clean_pycache test run runi debug debugi doc doc_html conf_git

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
	@echo 'run            : run main.py in debug mode'
	@echo 'runi           : run main.py in debug and interactive mode'
	@echo 'doc            : generate documentation both in pdf and html'
	@echo 'doc_html       : generate html documentation'
	@echo 'test           : execute all tests'
	@echo 'conf_git       : configure git hooks dir'

# Clean rules
clean: clean_doc clean_pycache

clean_doc: clean_doc_html

clean_doc_html:
	@rm -Rf docs/build/html

clean_pycache:
	@find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf


# === Normal rules ===========================================================
# Run rules
run:
	@PYTHONPATH=$PWD:$PYTHONPATH python -m progTiroc

runi:
	@PYTHONPATH=$PWD:$PYTHONPATH python -i -m progTiroc

debug:
	@FLASK_ENV=development DEBUG=1 PYTHONPATH=${PWD}:${PYTHONPATH} python -m progTiroc

debugi:
	@DEBUG=1 PYTHONPATH=${PWD}:${PYTHONPATH} python -m -i progTiroc


# === Dev rules ==============================================================
# Documentation rules
.sphinx_prep:
	@cd docs; sphinx-apidoc -f -o . ../progTiroc/;

doc: doc_html

doc_html:
	@echo ${@:4};
	@cd docs; $(MAKE) -j4 html;

# Test rules
test:
	@pytest; python-codacy-coverage -r coverage.xml

conf_git:
	@git config core.hooksPath hooks
