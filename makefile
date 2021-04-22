git:
	git add .
	git commit -m "$m"
	git push -u origin main

install:
	cp src/cesm_helper_scripts/gen_temp ~/.local/bin/
	cp src/cesm_helper_scripts/myncdump ~/.local/bin/
	cp src/cesm_helper_scripts/temp_plots ~/.local/bin/
