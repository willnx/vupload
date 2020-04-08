clean:
	-rm -rf build
	-rm -rf dist
	-rm -rf *.egg-info
	-rm -f tests/.coverage
	-docker rmi `docker images -q --filter "dangling=true"`

build: clean
	python setup.py bdist_wheel

install: build
	pip install -U dist/*.whl

uninstall:
	-pip uninstall -y vupload
