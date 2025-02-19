# Makefile

CC = gcc
CFLAGS = -Idrex/utils -I/usr/local/include -Wall
LDFLAGS = -L/usr/local/lib -lgsl -lgslcblas -lm

# List of object files
OBJS = drex/utils/prediction.o drex/utils/pareto_knee.o drex/utils/k_means_clustering.o drex/utils/combinations.o drex/utils/remove_node.o drex/schedulers/algorithm4.o drex/schedulers/bogdan_balance_penalty.o drex/schedulers/algorithm1.o drex/schedulers/random.o drex/schedulers/hdfs.o drex/schedulers/glusterfs.o drex/schedulers/optimal_schedule.o drex/schedulers/least_used_node.o

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

# Compile k_means_clustering.c
drex/utils/k_means_clustering.o: drex/utils/k_means_clustering.c drex/utils/k_means_clustering.h
	$(CC) $(CFLAGS) -c drex/utils/k_means_clustering.c -o drex/utils/k_means_clustering.o

# Compile combinations.c
drex/utils/combinations.o: drex/utils/combinations.c drex/utils/combinations.h
	$(CC) $(CFLAGS) -c drex/utils/combinations.c -o drex/utils/combinations.o

# Compile remove_node.c
drex/utils/remove_node.o: drex/utils/remove_node.c drex/utils/remove_node.h
	$(CC) $(CFLAGS) -c drex/utils/remove_node.c -o drex/utils/remove_node.o
	
# Compile bogdan_balance_penalty.c
drex/utils/bogdan_balance_penalty.o: drex/schedulers/bogdan_balance_penalty.c drex/schedulers/bogdan_balance_penalty.h
	$(CC) $(CFLAGS) -c drex/schedulers/bogdan_balance_penalty.c -o drex/schedulers/bogdan_balance_penalty.o

# Compile other schedulers
drex/schedulers/algorithm1.o: drex/schedulers/algorithm1.c drex/schedulers/algorithm1.h
	$(CC) $(CFLAGS) -c drex/schedulers/algorithm1.c -o drex/schedulers/algorithm1.o
drex/schedulers/random.o: drex/schedulers/random.c drex/schedulers/random.h
	$(CC) $(CFLAGS) -c drex/schedulers/random.c -o drex/schedulers/random.o
drex/schedulers/hdfs.o: drex/schedulers/hdfs.c drex/schedulers/hdfs.h
	$(CC) $(CFLAGS) -c drex/schedulers/hdfs.c -o drex/schedulers/hdfs.o
drex/schedulers/glusterfs.o: drex/schedulers/glusterfs.c drex/schedulers/glusterfs.h
	$(CC) $(CFLAGS) -c drex/schedulers/glusterfs.c -o drex/schedulers/glusterfs.o
drex/schedulers/optimal_schedule.o: drex/schedulers/optimal_schedule.c drex/schedulers/optimal_schedule.h
	$(CC) $(CFLAGS) -c drex/schedulers/optimal_schedule.c -o drex/schedulers/optimal_schedule.o
drex/schedulers/least_used_node.o: drex/schedulers/least_used_node.c drex/schedulers/least_used_node.h
	$(CC) $(CFLAGS) -c drex/schedulers/least_used_node.c -o drex/schedulers/least_used_node.o	
	
# Compile algorithm4.c
drex/schedulers/algorithm4.o: drex/schedulers/algorithm4.c drex/utils/prediction.h drex/utils/pareto_knee.h drex/utils/k_means_clustering.h drex/utils/combinations.h drex/schedulers/bogdan_balance_penalty.h drex/utils/remove_node.h drex/schedulers/algorithm1.h drex/schedulers/random.h drex/schedulers/hdfs.h drex/schedulers/glusterfs.h drex/schedulers/optimal_schedule.h drex/schedulers/least_used_node.h
	$(CC) $(CFLAGS) -c drex/schedulers/algorithm4.c -o drex/schedulers/algorithm4.o

# Clean up object files and the executable
clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean

