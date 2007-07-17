PKGNAME = iniparse
VERSION=$(shell awk '/Version:/ { print $$2 }' ${PKGNAME}.spec)


clean:
	rm -f *.pyc *.pyo *~ *.bak
	rm -f iniparse/*.pyc iniparse/*.pyo iniparse/*~ iniparse/*.bak
	rm -f *.tar.gz

archive:

	rm -rf ${PKGNAME}-${VERSION}.tar.gz
	rm -rf /tmp/${PKGNAME}-$(VERSION) /tmp/${PKGNAME}
	@dir=$$PWD; cd /tmp; cp -a "$$dir" ${PKGNAME}
	@mv /tmp/${PKGNAME} /tmp/${PKGNAME}-$(VERSION)
	@dir=$$PWD; cd /tmp; tar cvzf "$$dir/${PKGNAME}-$(VERSION).tar.gz" ${PKGNAME}-$(VERSION)
	@rm -rf /tmp/${PKGNAME}-$(VERSION)	
	@echo "The archive is in ${PKGNAME}-$(VERSION).tar.gz"


buildrpm: archive
	rpmbuild -ta ${PKGNAME}-$(VERSION).tar.gz
