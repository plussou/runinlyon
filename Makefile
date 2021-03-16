#----------------------------------------------------
#
#----------------------------------------------------

install_requirements:
	@pip install -r requirements.txt

install:
	@pip install .

install_dev:
	@pip install -e .

uninstall:
	@pip install -y runinlyon

test:
	@coverage run -m pytest -v tests/*.py
	@coverage report -m --omit=$(VIRTUAL_ENV)/lib/python*

clean:
	@rm -f */version.txt
	@rm -f *.log
	@rm -f */*.log
	@rm -f .coverage
	@rm -Rf .ipynb_checkpoints
	@rm -Rf notebooks/.ipynb_checkpoints
	@rm -Rf */__pycache__
	@rm -Rf */*.pyc
	@rm -Rf runinlyon.egg-info

all: install_requirements install test
