build:
	python setup.py build_ext --inplace

clean:
	rm -rf build core/*.c core/*.pyd module/*.c module/*.pyd