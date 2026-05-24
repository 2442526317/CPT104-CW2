#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "scheduler.h"

static void trim(char* str) {
    int len = strlen(str);
    while (len > 0 && isspace((unsigned char)str[len - 1])) {
        str[--len] = '\0';
    }
    int start = 0;
    while (str[start] && isspace((unsigned char)str[start])) {
        start++;
    }
    if (start > 0) {
        memmove(str, str + start, len - start + 1);
    }
}

static int count_words(const char* str) {
    int count = 0;
    int in_word = 0;
    while (*str) {
        if (isspace((unsigned char)*str)) {
            in_word = 0;
        } else {
            if (!in_word) {
                count++;
                in_word = 1;
            }
        }
        str++;
    }
    return count;
}

static int is_valid_integer(const char* str) {
    if (!str || *str == '\0') return 0;
    char* endptr;
    strtol(str, &endptr, 10);
    return *endptr == '\0';
}

int read_workload(const char* filename, Process** procs) {
    FILE* fp = fopen(filename, "r");
    if (!fp) return -1;

    char line[256];
    int count = 0;
    int capacity = 16;
    *procs = (Process*)malloc(capacity * sizeof(Process));
    
    if (!*procs) {
        fclose(fp);
        return -1;
    }
    
    while (fgets(line, sizeof(line), fp)) {
        trim(line);
        if (strlen(line) == 0 || line[0] == '#') {
            continue;
        }

        int word_count = count_words(line);
        if (word_count < 3 || word_count > 4) {
            fprintf(stderr, "Error: Invalid line format (expected 3 or 4 fields): '%s'\n", line);
            fclose(fp);
            free(*procs);
            exit(1);
        }

        char pid_raw[64], arrival_str[32], burst_str[32], priority_str[32];
        
        int fields = sscanf(line, "%63s %31s %31s %31s", pid_raw, arrival_str, burst_str, priority_str);
        
        if (fields != word_count) {
            fprintf(stderr, "Error: Cannot parse all fields: '%s'\n", line);
            fclose(fp);
            free(*procs);
            exit(1);
        }

        if (strlen(pid_raw) >= MAX_PID_LEN) {
            fprintf(stderr, "Error: PID too long (max %d chars): '%s'\n", MAX_PID_LEN - 1, line);
            fclose(fp);
            free(*procs);
            exit(1);
        }

        if (!is_valid_integer(arrival_str) || !is_valid_integer(burst_str)) {
            fprintf(stderr, "Error: arrival_time and burst_time must be integers: '%s'\n", line);
            fclose(fp);
            free(*procs);
            exit(1);
        }

        if (word_count == 4 && !is_valid_integer(priority_str)) {
            fprintf(stderr, "Error: priority must be an integer: '%s'\n", line);
            fclose(fp);
            free(*procs);
            exit(1);
        }

        Process p;
        strncpy(p.pid, pid_raw, MAX_PID_LEN - 1);
        p.pid[MAX_PID_LEN - 1] = '\0';
        p.arrival_time = atoi(arrival_str);
        p.burst_time = atoi(burst_str);
        p.priority = (word_count == 4) ? atoi(priority_str) : 0;
        p.is_completed = 0;
        p.first_run = 1;
        p.start_time = -1;

        if (strlen(p.pid) == 0) {
            fprintf(stderr, "Error: PID cannot be empty: '%s'\n", line);
            fclose(fp);
            free(*procs);
            exit(1);
        }

        if (p.arrival_time < 0) {
            fprintf(stderr, "Error: arrival_time must be non-negative: '%s'\n", line);
            fclose(fp);
            free(*procs);
            exit(1);
        }

        if (p.burst_time <= 0) {
            fprintf(stderr, "Error: burst_time must be positive: '%s'\n", line);
            fclose(fp);
            free(*procs);
            exit(1);
        }

        if (count >= capacity) {
            capacity *= 2;
            Process* new_procs = (Process*)realloc(*procs, capacity * sizeof(Process));
            if (!new_procs) {
                fclose(fp);
                free(*procs);
                *procs = NULL;
                return -1;
            }
            *procs = new_procs;
        }

        p.remaining_time = p.burst_time;
        (*procs)[count++] = p;
    }

    fclose(fp);
    return count;
}

int calculate_context_switches(int* timeline, int total_ticks) {
    int context_switches = 0;
    int last_pid = -1;
    
    for (int i = 0; i < total_ticks; i++) {
        int current_pid = timeline[i];
        if (last_pid != -1 && current_pid != -1 && last_pid != current_pid) {
            context_switches++;
        }
        last_pid = current_pid;
    }
    
    return context_switches;
}

void print_gantt_and_stats(Process* procs, int n, const char* alg, int* gantt_timeline, int total_ticks) {
    if (total_ticks > 0) {
        printf("GANTT: 0");
        int i = 0;
        
        while (i < total_ticks) {
            int run_id = gantt_timeline[i];
            while (i < total_ticks && gantt_timeline[i] == run_id) {
                i++;
            }
            if (run_id == -1) {
                printf(" | IDLE | %d", i);
            } else {
                printf(" | %s | %d", procs[run_id].pid, i);
            }
        }
        printf("\n");
    }

    printf("\nPID\tArrival\tBurst\tStart\tFinish\tWaiting\tTurnaround\tResponse\n");
    double total_wait = 0, total_tat = 0, total_resp = 0;
    int busy_ticks = 0;

    for (int i = 0; i < n; i++) {
        total_wait += procs[i].wait_time;
        total_tat += procs[i].turnaround_time;
        total_resp += procs[i].response_time;
        busy_ticks += procs[i].burst_time;

        printf("%s\t%d\t%d\t%d\t%d\t%d\t%d\t\t%d\n",
               procs[i].pid, procs[i].arrival_time, procs[i].burst_time,
               procs[i].start_time, procs[i].end_time, procs[i].wait_time,
               procs[i].turnaround_time, procs[i].response_time);
    }

    double cpu_util = total_ticks > 0 ? ((double)busy_ticks / total_ticks) * 100.0 : 0.0;
    int context_switches = calculate_context_switches(gantt_timeline, total_ticks);
    
    printf("\nRESULT: OK\n");
    printf("ALG=%s\n", alg);
    printf("AVG_WAIT=%.2f\n", total_wait / n);
    printf("AVG_TAT=%.2f\n", total_tat / n);
    printf("AVG_RESP=%.2f\n", total_resp / n);
    printf("CONTEXT_SWITCHES=%d\n", context_switches);
    printf("CPU_UTIL=%.2f%%\n", cpu_util);
}
