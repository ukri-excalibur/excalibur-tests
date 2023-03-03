
pdf:
	mkdir -p build/
	python make_plots.py
	mv all_data.csv build/
	cp report.tex build/
	cd build; pdflatex report.tex; cp report.pdf ../

clean:
	rm -rf build
