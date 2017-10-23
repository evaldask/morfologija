.PHONY: all
all: bin/morfologija

bin/python:
	virtualenv --no-site-packages --python=python3 .
	bin/pip install --upgrade setuptools

bin/buildout: bin/python
	bin/python bootstrap.py

bin/morfologija: bin/buildout setup.py buildout.cfg
	bin/buildout -N

.PHONY: tags
tags:
	bin/tags --ctags-vi

.PHONY: clean
clean:
	rm -rf \
	    .installed.cfg \
	    .mr.developer.cfg \
	    bin \
	    develop-eggs \
	    include \
	    lib \
	    local \
	    share
