#ifndef SCHEDULER_H
#define SCHEDULER_H

#define MAX_PID_LEN 16

typedef struct {
    char pid[MAX_PID_LEN];
    int arrival_time;
    int burst_time;
    int remaining_time;
    int priority;
    
    int start_time;
    int end_time;
    int wait_time;
    int turnaround_time;
    int response_time;
    
    int is_completed;
    int first_run;
} Process;

void run_fcfs(Process* procs, int n);
void run_sjf(Process* procs, int n);
void run_srtf(Process* procs, int n);
void run_rr(Process* procs, int n, int quantum);

int read_workload(const char* filename, Process** procs);
void print_gantt_and_stats(Process* procs, int n, const char* alg, int* gantt_timeline, int total_ticks);
int calculate_context_switches(int* timeline, int total_ticks);

#endif
