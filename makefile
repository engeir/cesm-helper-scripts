MY_VAR := $(shell python -c "import sys;print(sys.executable)")

git:
	git add .
	git commit -m "$m"
	git push -u origin main

install:
	cp src/cesm_helper_scripts/gen_agg ~/.local/bin/ && chmod +x ~/.local/bin/gen_agg

autoinstall:
	cp src/cesm_helper_scripts/gen_agg ~/.local/bin/ && chmod +x ~/.local/bin/gen_agg
	sed -i '1s|.*|#!$(MY_VAR)|' ~/.local/bin/gen_agg
