PRIMARIES:=thesis.pdf
BUILDDIR:=.build
EXTRADIRS:=chapters literature figures

ROOTTEXFILES:=$(wildcard *.tex)
LIGHTTEXFILES:=$(patsubst %,$(BUILDDIR)/%,$(ROOTTEXFILES))
LIGHTFILES:=$(LIGHTTEXFILES) $(patsubst %,$(BUILDDIR)/%,$(EXTRADIRS))

.PHONY:all
all:$(PRIMARIES)

$(PRIMARIES):%.pdf:$(BUILDDIR)/%.pdf
	cp '$<' .

$(BUILDDIR):
	mkdir -p '$(BUILDDIR)'

$(patsubst %,$(BUILDDIR)/%,$(PRIMARIES)):%:$(BUILDDIR) $(LIGHTFILES)
	cd $(BUILDDIR); latexmk -pdf $(patsubst $(BUILDDIR)/%.pdf,%.tex,$@)

$(LIGHTFILES): $(BUILDDIR)/%: %
	cp -r '$<' '$(dir $@)'

.PHONY:almostclean-sub
almostclean-sub:
	cd '$(BUILDDIR)'; rm *.aux *.log *.out *.fdb_latexmk; true

.PHONY:clean-sub
clean-sub:
	cd '$(BUILDDIR)'; rm *.aux *.log *.out *.pdf *.fdb_latexmk; true

.PHONY:almostclean
almostclean:almostclean-sub

.PHONY:clean
clean:clean-sub
	for f in $(PRIMARIES); do [ -f "$$f" ] && rm "$$f"; done
