build:
	"$(PYTHON3)" setup.py build_ext --inplace

clean:
	rm -rf build */*.c */*.pyd */*.so
