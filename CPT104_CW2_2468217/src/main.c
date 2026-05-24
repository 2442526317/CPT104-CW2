#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "scheduler.h"

void run_demo() {
    printf("===========================================\n");
    
    Process demo_data_1[] = {
        {"P1", 0, 8, 8, 1, -1, 0, 0, 0, 0, 0, 1},
        {"P2", 1, 4, 4, 2, -1, 0, 0, 0, 0, 0, 1},
        {"P3", 2, 9, 9, 3, -1, 0, 0, 0, 0, 0, 1},
        {"P4", 3, 5, 5, 4, -1, 0, 0, 0, 0, 0, 1}
    };
    
    Process demo_data_2[] = {
        {"P1", 0, 8, 8, 1, -1, 0, 0, 0, 0, 0, 1},
        {"P2", 1, 4, 4, 2, -1, 0, 0, 0, 0, 0, 1},
        {"P3", 2, 9, 9, 3, -1, 0, 0, 0, 0, 0, 1},
        {"P4", 3, 5, 5, 4, -1, 0, 0, 0, 0, 0, 1}
    };
    
    Process* demo_procs_1 = (Process*)malloc(4 * sizeof(Process));
    Process* demo_procs_2 = (Process*)malloc(4 * sizeof(Process));
    
    if (!demo_procs_1 || !demo_procs_2) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        exit(1);
    }
    
    memcpy(demo_procs_1, demo_data_1, 4 * sizeof(Process));
    memcpy(demo_procs_2, demo_data_2, 4 * sizeof(Process));

    printf("\n>>> Running Demo Algorithm 1: FCFS <<<\n");
    run_fcfs(demo_procs_1, 4);

    printf("\n>>> Running Demo Algorithm 2: RR (Quantum = 3) <<<\n");
    run_rr(demo_procs_2, 4, 3);
    printf("===========================================\n");
    
    free(demo_procs_1);
    free(demo_procs_2);
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Error: Missing arguments.\n");
        return 1;
    }

    if (strcmp(argv[1], "--demo") == 0) {
        run_demo();
        return 0;
    }

    char* filename = argv[1];
    char* alg = NULL;
    int quantum = -1;

    for (int i = 2; i < argc; i++) {
        if (strcmp(argv[i], "--alg") == 0 && i + 1 < argc) {
            alg = argv[i + 1];
            i++;
        } else if ((strcmp(argv[i], "-q") == 0 || strcmp(argv[i], "--q") == 0) && i + 1 < argc) {
            quantum = atoi(argv[i + 1]);
            i++;
        }
    }

    if (!alg) {
        fprintf(stderr, "Error: Option --alg is mandatory unless running --demo.\n");
        return 1;
    }

    if (strcmp(alg, "RR") == 0 && quantum <= 0) {
        fprintf(stderr, "Error: RR algorithm requires quantum parameter --q [value] > 0.\n");
        return 1;
    }

    Process* procs = NULL;
    int n = read_workload(filename, &procs);
    if (n <= 0) {
        fprintf(stderr, "Error: Failed to read workload from %s\n", filename);
        return 1;
    }

    if (strcmp(alg, "FCFS") == 0) {
        run_fcfs(procs, n);
    } else if (strcmp(alg, "SJF") == 0) {
        run_sjf(procs, n);
    } else if (strcmp(alg, "SRTF") == 0) {
        run_srtf(procs, n);
    } else if (strcmp(alg, "RR") == 0) {
        run_rr(procs, n, quantum);
    } else {
        fprintf(stderr, "Error: Unknown algorithm '%s'.\n", alg);
        free(procs);
        return 1;
    }

    free(procs);
    return 0;
}
