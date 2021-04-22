git:
	git add .
	git commit -m "$m"
	git push -u origin main

install:
	cp src/cesm_helper_scripts/gen_temp ~/.local/bin/ && chmod +x ~/.local/bin/gen_temp
	cp src/cesm_helper_scripts/myncdump ~/.local/bin/ && chmod +x ~/.local/bin/myncdump
	cp src/cesm_helper_scripts/temp_plots ~/.local/bin/ && chmod +x ~/.local/bin/temp_plots
