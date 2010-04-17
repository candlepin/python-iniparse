PKGNAME = iniparse
SPECVERSION=$(shell awk '/Version:/ { print $$2 }' python-${PKGNAME}.spec)
SETUPVERSION=$(shell awk -F\' '/VERSION =/ { print $$2 }' setup.py)

clean:
	rm -f *.pyc *.pyo *~ *.bak
	rm -f iniparse/*.pyc iniparse/*.pyo iniparse/*~ iniparse/*.bak
	rm -f tests/*.pyc tests/*.pyo tests/*~ tests/*.bak
	rm -f *.tar.gz MANIFEST

archive:
	python setup.py sdist -d .
	@echo "The archive is in ${PKGNAME}-$(SETUPVERSION).tar.gz"

rpmbuild: archive
	rpmbuild -ta ${PKGNAME}-$(SPECVERSION).tar.gz

pychecker:
	pychecker --stdlib iniparse/*py tests/*py
