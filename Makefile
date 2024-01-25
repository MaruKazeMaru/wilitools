CC=gcc
TARGETNAME=hmm
SRCS=hmm.c
SRCDIR=csrc
OBJDIR=cbuild/obj
INCDIR=cinclude

$(OBJDIR)/lib$(TARGETNAME).so: $(addprefix $(SRCDIR)/, $(SRCS))
	@mkdir -p $(OBJDIR)
	$(CC) -I$(INCDIR) -lm -shared -fPIC $^ -o $@
