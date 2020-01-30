#include <mpi.h>
#include <stdio.h>
#include <unistd.h>
#include <time.h>

int main(int argc, char** argv) {
    
    time_t timer;
    char buffer[26];
    struct tm* tm_info;

    // Initialize the MPI environment
    MPI_Init(NULL, NULL);
    
    // Get the number of processes
    int world_size;
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);
    // Get the rank of the process
    int world_rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
    // Get the name of the processor
    char processor_name[MPI_MAX_PROCESSOR_NAME];
    int name_len;
    MPI_Get_processor_name(processor_name, &name_len);
    
    for (;;) {
      timer = time(NULL);
      tm_info = localtime(&timer);
      
      strftime(buffer, 26, "%Y-%m-%d %H:%M:%S", tm_info);
      
      // Print off a hello world message
      printf("%s: Hello world from processor %s, rank %d out of %d processors\n",
      buffer, processor_name, world_rank, world_size);
      sleep(30);      
    }

    // Finalize the MPI environment.
    MPI_Finalize();
}                                                                       
