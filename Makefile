build:
	python3 setup.py build_ext --inplace

clean:
	rm -rf build core/*.c core/*.pyd core/*.so module/*.c module/*.pyd module/*.so
