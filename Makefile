CC=gcc
TARGETNAME=wilihmm
TARGETLIB=lib$(TARGETNAME).so
SRCS=hmm.c
SRCDIR=csrc
BUILDDIR=cbuild
OBJDIR=$(BUILDDIR)/obj
INCDIR=cinclude

TARGET=$(OBJDIR)/$(TARGETLIB)

$(TARGET): $(addprefix $(SRCDIR)/, $(SRCS))
	@mkdir -p $(OBJDIR)
	$(CC) -I$(INCDIR) -lm -shared -fPIC $^ -o $@

clean:
	rm -rf $(BUILDDIR)
