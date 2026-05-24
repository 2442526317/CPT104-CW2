CC = gcc
CFLAGS = -Wall -Wextra -O2
SRC = src/main.c src/algorithms.c src/utils.c
OBJ = $(SRC:.c=.o)
TARGET = sched

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJ)

clean:
	rm -f $(OBJ) $(TARGET)
