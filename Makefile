PKG_NAME=iniparse
SPEC_VERSION=$(shell awk '/Version:/ { print $$2 }' python-${PKG_NAME}.spec)
SETUP_VERSION=$(shell awk '/VERSION =/ { print $$3 }' setup.py)

clean:
	rm -f *.pyc *.pyo *~ *.bak
	rm -f iniparse/*.pyc iniparse/*.pyo iniparse/*~ iniparse/*.bak
	rm -f tests/*.pyc tests/*.pyo tests/*~ tests/*.bak
	rm -f *.tar.gz MANIFEST

archive:
	python setup.py sdist -d .
	mv ${PKG_NAME}-${SETUP_VERSION}.tar.gz python-${PKG_NAME}-${SETUP_VERSION}.tar.gz
	@echo "The archive is in python-${PKG_NAME}-${SETUP_VERSION}.tar.gz"

rpmbuild: archive
	rpmbuild -ta python-${PKG_NAME}-$(SPEC_VERSION).tar.gz

pychecker:
	pychecker --stdlib iniparse/*py tests/*py
