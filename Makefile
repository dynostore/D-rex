# Makefile

CC = gcc
CFLAGS = -Idrex/utils -I/usr/local/include -Wall
LDFLAGS = -L/usr/local/lib -lgsl -lgslcblas -lm

# List of object files
OBJS = drex/utils/prediction.o drex/utils/pareto_knee.o drex/schedulers/algorithm4.o

# Target executable
TARGET = alg4

# Default target
all: $(TARGET)

# Link the target executable
$(TARGET): $(OBJS)
	$(CC) -o $(TARGET) $(OBJS) $(LDFLAGS)

# Compile prediction.c
drex/utils/prediction.o: drex/utils/prediction.c drex/utils/prediction.h
	$(CC) $(CFLAGS) -c drex/utils/prediction.c -o drex/utils/prediction.o

# Compile pareto_knee.c
drex/utils/pareto_knee.o: drex/utils/pareto_knee.c drex/utils/pareto_knee.h
	$(CC) $(CFLAGS) -c drex/utils/pareto_knee.c -o drex/utils/pareto_knee.o
	
# Compile algorithm4.c
drex/schedulers/algorithm4.o: drex/schedulers/algorithm4.c drex/utils/prediction.h drex/utils/pareto_knee.h
	$(CC) $(CFLAGS) -c drex/schedulers/algorithm4.c -o drex/schedulers/algorithm4.o

# Clean up object files and the executable
clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean

