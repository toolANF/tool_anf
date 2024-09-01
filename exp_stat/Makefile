CC:=g++
SRCDIR := src
BUILDDIR := build

CFLAGS := -O3 -mtune=native -march=native -Wall -Wno-unused-variable -std=c++17 -DNDEBUG -fopenmp

TARGET := experiments

SOURCES := $(shell find $(SRCDIR) -type f -name *.cpp)
HEADERS := $(shell find $(SRCDIR) -type f -name *.hpp)

OBJECTS := $(patsubst $(SRCDIR)/%,$(BUILDDIR)/%,$(SOURCES:.cpp=.o))

DEPS := $(patsubst $(SRCDIR)/%,$(BUILDDIR)/%,$(SOURCES:.cpp=.deps))

all: $(TARGET)

$(TARGET): $(OBJECTS)
	@echo " Linking GDSSearch..."; $(CC) $(USERDEFINES) $(CFLAGS) $^ $(LIBS) -o $(TARGET)

$(BUILDDIR)/%.o: $(SRCDIR)/%.cpp  $(HEADERS)
	@mkdir -p $(BUILDDIR)
	@echo " CC $<"; $(CC) $(USERDEFINES) $(CFLAGS) -MD -MF $(@:.o=.deps) -c -o $@ $<

clean:
	@echo " Cleaning..."; $(RM) -r $(BUILDDIR) $(TARGET) *~ *.csv

-include $(DEPS)

.PHONY: clean 

run: $(TARGET)
	@echo " Running $(TARGET)..."; ./$(TARGET)

