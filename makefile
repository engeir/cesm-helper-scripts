MY_VAR := $(shell python -c "import sys;print(sys.executable)")

install:
	cp src/cesm_helper_scripts/gen_agg ~/.local/bin/ && chmod +x ~/.local/bin/gen_agg

autoinstall:
	cp src/cesm_helper_scripts/gen_agg ~/.local/bin/ && chmod +x ~/.local/bin/gen_agg
	sed -i '1s|.*|#!$(MY_VAR)|' ~/.local/bin/gen_agg
