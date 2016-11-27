deploy:
	if [ -d dist ]; then rm -rf dist; fi
	python setup.py bdist_wheel
	twine upload dist/*

