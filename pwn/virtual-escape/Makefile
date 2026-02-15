CC = gcc
CFLAGS = -Wall -Wextra -g
TARGET = vm

# Choose difficulty level:
# EASY: No PIE, no canary, win() function available
# MEDIUM: No PIE, with canary
# HARD: PIE + canary + full RELRO

# Default: EASY mode
DIFFICULTY ?= EASY

ifeq ($(DIFFICULTY),EASY)
    LDFLAGS = -no-pie -fno-stack-protector -z execstack
    $(info Building EASY mode: no PIE, no stack protector, NX disabled)
else ifeq ($(DIFFICULTY),MEDIUM)
    LDFLAGS = -no-pie -fstack-protector
    $(info Building MEDIUM mode: no PIE, with stack protector)
else ifeq ($(DIFFICULTY),HARD)
    LDFLAGS = -pie -fPIE -fstack-protector -z now -z relro
    $(info Building HARD mode: PIE + stack protector + full RELRO)
else
    $(error Unknown DIFFICULTY level. Use EASY, MEDIUM, or HARD)
endif

SOURCES = src/main.c src/vm.c
OBJECTS = $(SOURCES:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^
	@echo "Built $(TARGET) with $(DIFFICULTY) difficulty"

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(TARGET) $(OBJECTS)

easy:
	$(MAKE) DIFFICULTY=EASY

medium:
	$(MAKE) DIFFICULTY=MEDIUM

hard:
	$(MAKE) DIFFICULTY=HARD

.PHONY: all clean easy medium hard
