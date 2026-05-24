#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "scheduler.h"

int compare_procs(const void* a, const void* b) {
    Process* p1 = (Process*)a;
    Process* p2 = (Process*)b;
    if (p1->arrival_time != p2->arrival_time) {
        return p1->arrival_time - p2->arrival_time;
    }
    return strcmp(p1->pid, p2->pid);
}

int get_next_process(Process* procs, int n, int current_time, int is_srtf) {
    int best_index = -1;
    for (int i = 0; i < n; i++) {
        if (procs[i].is_completed || procs[i].arrival_time > current_time) {
            continue;
        }
        if (best_index == -1) {
            best_index = i;
        } else {
            if (is_srtf) {
                if (procs[i].remaining_time < procs[best_index].remaining_time) {
                    best_index = i;
                } else if (procs[i].remaining_time == procs[best_index].remaining_time) {
                    if (procs[i].arrival_time < procs[best_index].arrival_time) {
                        best_index = i;
                    } else if (procs[i].arrival_time == procs[best_index].arrival_time) {
                        if (strcmp(procs[i].pid, procs[best_index].pid) < 0) {
                            best_index = i;
                        }
                    }
                }
            } else {
                if (procs[i].burst_time < procs[best_index].burst_time) {
                    best_index = i;
                } else if (procs[i].burst_time == procs[best_index].burst_time) {
                    if (procs[i].arrival_time < procs[best_index].arrival_time) {
                        best_index = i;
                    } else if (procs[i].arrival_time == procs[best_index].arrival_time) {
                        if (strcmp(procs[i].pid, procs[best_index].pid) < 0) {
                            best_index = i;
                        }
                    }
                }
            }
        }
    }
    return best_index;
}

void run_fcfs(Process* procs, int n) {
    qsort(procs, n, sizeof(Process), compare_procs);
    
    int total_burst = 0;
    int max_arrival = 0;
    for (int i = 0; i < n; i++) {
        total_burst += procs[i].burst_time;
        if (procs[i].arrival_time > max_arrival) {
            max_arrival = procs[i].arrival_time;
        }
    }
    int timeline_size = total_burst + max_arrival + 1;
    int* timeline = (int*)malloc(timeline_size * sizeof(int));
    
    if (!timeline) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        exit(1);
    }
    
    int current_time = 0;

    for (int i = 0; i < n; i++) {
        if (current_time < procs[i].arrival_time) {
            while (current_time < procs[i].arrival_time) {
                timeline[current_time++] = -1;
            }
        }

        procs[i].start_time = current_time;
        procs[i].response_time = procs[i].start_time - procs[i].arrival_time;
        
        for (int j = 0; j < procs[i].burst_time; j++) {
            timeline[current_time++] = i;
        }
        
        procs[i].end_time = current_time;
        procs[i].turnaround_time = procs[i].end_time - procs[i].arrival_time;
        procs[i].wait_time = procs[i].turnaround_time - procs[i].burst_time;
        procs[i].is_completed = 1;
    }

    print_gantt_and_stats(procs, n, "FCFS", timeline, current_time);
    free(timeline);
}

void run_sjf(Process* procs, int n) {
    int total_burst = 0;
    int max_arrival = 0;
    for (int i = 0; i < n; i++) {
        total_burst += procs[i].burst_time;
        if (procs[i].arrival_time > max_arrival) {
            max_arrival = procs[i].arrival_time;
        }
    }
    int timeline_size = total_burst + max_arrival + 1;
    int* timeline = (int*)malloc(timeline_size * sizeof(int));
    
    if (!timeline) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        exit(1);
    }
    
    int current_time = 0;
    int completed_count = 0;

    while (completed_count < n) {
        int idx = get_next_process(procs, n, current_time, 0);

        if (idx == -1) {
            timeline[current_time++] = -1;
            continue;
        }

        procs[idx].start_time = current_time;
        procs[idx].response_time = procs[idx].start_time - procs[idx].arrival_time;

        for (int j = 0; j < procs[idx].burst_time; j++) {
            timeline[current_time++] = idx;
        }

        procs[idx].end_time = current_time;
        procs[idx].turnaround_time = procs[idx].end_time - procs[idx].arrival_time;
        procs[idx].wait_time = procs[idx].turnaround_time - procs[idx].burst_time;
        procs[idx].is_completed = 1;
        
        completed_count++;
    }

    print_gantt_and_stats(procs, n, "SJF", timeline, current_time);
    free(timeline);
}

void run_srtf(Process* procs, int n) {
    int total_burst = 0;
    int max_arrival = 0;
    for (int i = 0; i < n; i++) {
        total_burst += procs[i].burst_time;
        if (procs[i].arrival_time > max_arrival) {
            max_arrival = procs[i].arrival_time;
        }
    }
    int timeline_size = total_burst + max_arrival + 1;
    int* timeline = (int*)malloc(timeline_size * sizeof(int));
    
    if (!timeline) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        exit(1);
    }
    
    int current_time = 0;
    int completed_count = 0;

    while (completed_count < n) {
        int idx = get_next_process(procs, n, current_time, 1);

        if (idx == -1) {
            timeline[current_time++] = -1;
            continue;
        }

        if (procs[idx].first_run) {
            procs[idx].start_time = current_time;
            procs[idx].response_time = procs[idx].start_time - procs[idx].arrival_time;
            procs[idx].first_run = 0;
        }

        timeline[current_time++] = idx;
        procs[idx].remaining_time--;

        if (procs[idx].remaining_time == 0) {
            procs[idx].end_time = current_time;
            procs[idx].turnaround_time = procs[idx].end_time - procs[idx].arrival_time;
            procs[idx].wait_time = procs[idx].turnaround_time - procs[idx].burst_time;
            procs[idx].is_completed = 1;
            completed_count++;
        }
    }

    print_gantt_and_stats(procs, n, "SRTF", timeline, current_time);
    free(timeline);
}

void run_rr(Process* procs, int n, int quantum) {
    qsort(procs, n, sizeof(Process), compare_procs);

    int total_burst = 0;
    int max_arrival = 0;
    for (int i = 0; i < n; i++) {
        total_burst += procs[i].burst_time;
        if (procs[i].arrival_time > max_arrival) {
            max_arrival = procs[i].arrival_time;
        }
    }
    int timeline_size = total_burst + max_arrival + 1;
    int* timeline = (int*)malloc(timeline_size * sizeof(int));
    
    if (!timeline) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        exit(1);
    }
    
    int current_time = 0;
    int completed_count = 0;

    int queue_capacity = n * 4;
    int* queue = (int*)malloc(queue_capacity * sizeof(int));
    int* in_queue = (int*)calloc(n, sizeof(int));
    
    if (!queue || !in_queue) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        exit(1);
    }
    
    int head = 0, tail = 0;
    int running_idx = -1;

    while (completed_count < n) {
        for (int i = 0; i < n; i++) {
            if (!procs[i].is_completed && procs[i].arrival_time <= current_time && !in_queue[i] && i != running_idx) {
                int next_tail = (tail + 1) % queue_capacity;
                if (next_tail != head) {
                    queue[tail] = i;
                    tail = next_tail;
                    in_queue[i] = 1;
                } else {
                    fprintf(stderr, "Warning: RR queue is full, process %s may be delayed\n", procs[i].pid);
                }
            }
        }

        if (head == tail && running_idx == -1) {
            timeline[current_time++] = -1;
            continue;
        }

        if (running_idx == -1) {
            running_idx = queue[head];
            head = (head + 1) % queue_capacity;
            in_queue[running_idx] = 0;

            if (procs[running_idx].first_run) {
                procs[running_idx].start_time = current_time;
                procs[running_idx].response_time = procs[running_idx].start_time - procs[running_idx].arrival_time;
                procs[running_idx].first_run = 0;
            }
        }

        int slice = (procs[running_idx].remaining_time < quantum) ? procs[running_idx].remaining_time : quantum;
        
        for (int step = 0; step < slice; step++) {
            timeline[current_time + step] = running_idx;
        }
        
        for (int step = 1; step <= slice; step++) {
            int check_t = current_time + step;
            for (int i = 0; i < n; i++) {
                if (!procs[i].is_completed && procs[i].arrival_time <= check_t && !in_queue[i] && i != running_idx) {
                    int next_tail = (tail + 1) % queue_capacity;
                    if (next_tail != head) {
                        queue[tail] = i;
                        tail = next_tail;
                        in_queue[i] = 1;
                    }
                }
            }
        }

        current_time += slice;
        procs[running_idx].remaining_time -= slice;

        if (procs[running_idx].remaining_time == 0) {
            procs[running_idx].end_time = current_time;
            procs[running_idx].turnaround_time = procs[running_idx].end_time - procs[running_idx].arrival_time;
            procs[running_idx].wait_time = procs[running_idx].turnaround_time - procs[running_idx].burst_time;
            procs[running_idx].is_completed = 1;
            completed_count++;
            running_idx = -1;
        } else {
            int next_tail = (tail + 1) % queue_capacity;
            if (next_tail != head) {
                queue[tail] = running_idx;
                tail = next_tail;
                in_queue[running_idx] = 1;
            } else {
                fprintf(stderr, "Warning: RR queue is full, process %s may be delayed\n", procs[running_idx].pid);
            }
            running_idx = -1;
        }
    }

    print_gantt_and_stats(procs, n, "RR", timeline, current_time);
    free(timeline);
    free(queue);
    free(in_queue);
}
