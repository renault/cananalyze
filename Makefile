RUN=python3
.PHONY: all
#TESTMODULES=$(patsubst %.py, %.py, $(wildcard tests/unittest_*.py))

doc:
	cd docs && make html

clean_doc:
	cd docs && make clean

clean: clean_doc
	find ./ -name "*.pyc" -exec rm {} \;
	rm -rf build cananalyze.egg-info dist
install:
	${RUN} setup.py build
	${RUN} setup.py install

test:
	${RUN} tests/unittest_pycan.py
	${RUN} tests/unittest_isotp.py
	${RUN} tests/unittest_uds.py
	${RUN} tests/unittest_dbi.py
	${RUN} tests/unittest_scan.py 
	${RUN} tests/unittest_sa.py 
	${RUN} tests/unittest_gwcalibration.py

all: doc

publish:
	sh publish.sh
