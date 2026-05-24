import os

project_dirs = ["src"]

files = {
    "src/scheduler.h": """#ifndef SCHEDULER_H
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
""",

    "src/main.c": """#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "scheduler.h"

void run_demo() {
    printf("===========================================\\n");
    
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
        fprintf(stderr, "Error: Memory allocation failed\\n");
        exit(1);
    }
    
    memcpy(demo_procs_1, demo_data_1, 4 * sizeof(Process));
    memcpy(demo_procs_2, demo_data_2, 4 * sizeof(Process));

    printf("\\n>>> Running Demo Algorithm 1: FCFS <<<\\n");
    run_fcfs(demo_procs_1, 4);

    printf("\\n>>> Running Demo Algorithm 2: RR (Quantum = 3) <<<\\n");
    run_rr(demo_procs_2, 4, 3);
    printf("===========================================\\n");
    
    free(demo_procs_1);
    free(demo_procs_2);
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Error: Missing arguments.\\n");
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
        fprintf(stderr, "Error: Option --alg is mandatory unless running --demo.\\n");
        return 1;
    }

    if (strcmp(alg, "RR") == 0 && quantum <= 0) {
        fprintf(stderr, "Error: RR algorithm requires quantum parameter --q [value] > 0.\\n");
        return 1;
    }

    Process* procs = NULL;
    int n = read_workload(filename, &procs);
    if (n <= 0) {
        fprintf(stderr, "Error: Failed to read workload from %s\\n", filename);
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
        fprintf(stderr, "Error: Unknown algorithm '%s'.\\n", alg);
        free(procs);
        return 1;
    }

    free(procs);
    return 0;
}
""",

    "src/utils.c": """#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "scheduler.h"

static void trim(char* str) {
    int len = strlen(str);
    while (len > 0 && isspace((unsigned char)str[len - 1])) {
        str[--len] = '\\0';
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
    if (!str || *str == '\\0') return 0;
    char* endptr;
    strtol(str, &endptr, 10);
    return *endptr == '\\0';
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
            fprintf(stderr, "Error: Invalid line format (expected 3 or 4 fields): '%s'\\n", line);
            fclose(fp);
            free(*procs);
            exit(1);
        }

        char pid_raw[64], arrival_str[32], burst_str[32], priority_str[32];
        
        int fields = sscanf(line, "%63s %31s %31s %31s", pid_raw, arrival_str, burst_str, priority_str);
        
        if (fields != word_count) {
            fprintf(stderr, "Error: Cannot parse all fields: '%s'\\n", line);
            fclose(fp);
            free(*procs);
            exit(1);
        }

        if (strlen(pid_raw) >= MAX_PID_LEN) {
            fprintf(stderr, "Error: PID too long (max %d chars): '%s'\\n", MAX_PID_LEN - 1, line);
            fclose(fp);
            free(*procs);
            exit(1);
        }

        if (!is_valid_integer(arrival_str) || !is_valid_integer(burst_str)) {
            fprintf(stderr, "Error: arrival_time and burst_time must be integers: '%s'\\n", line);
            fclose(fp);
            free(*procs);
            exit(1);
        }

        if (word_count == 4 && !is_valid_integer(priority_str)) {
            fprintf(stderr, "Error: priority must be an integer: '%s'\\n", line);
            fclose(fp);
            free(*procs);
            exit(1);
        }

        Process p;
        strncpy(p.pid, pid_raw, MAX_PID_LEN - 1);
        p.pid[MAX_PID_LEN - 1] = '\\0';
        p.arrival_time = atoi(arrival_str);
        p.burst_time = atoi(burst_str);
        p.priority = (word_count == 4) ? atoi(priority_str) : 0;
        p.is_completed = 0;
        p.first_run = 1;
        p.start_time = -1;

        if (strlen(p.pid) == 0) {
            fprintf(stderr, "Error: PID cannot be empty: '%s'\\n", line);
            fclose(fp);
            free(*procs);
            exit(1);
        }

        if (p.arrival_time < 0) {
            fprintf(stderr, "Error: arrival_time must be non-negative: '%s'\\n", line);
            fclose(fp);
            free(*procs);
            exit(1);
        }

        if (p.burst_time <= 0) {
            fprintf(stderr, "Error: burst_time must be positive: '%s'\\n", line);
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
        printf("\\n");
    }

    printf("\\nPID\\tArrival\\tBurst\\tStart\\tFinish\\tWaiting\\tTurnaround\\tResponse\\n");
    double total_wait = 0, total_tat = 0, total_resp = 0;
    int busy_ticks = 0;

    for (int i = 0; i < n; i++) {
        total_wait += procs[i].wait_time;
        total_tat += procs[i].turnaround_time;
        total_resp += procs[i].response_time;
        busy_ticks += procs[i].burst_time;

        printf("%s\\t%d\\t%d\\t%d\\t%d\\t%d\\t%d\\t\\t%d\\n",
               procs[i].pid, procs[i].arrival_time, procs[i].burst_time,
               procs[i].start_time, procs[i].end_time, procs[i].wait_time,
               procs[i].turnaround_time, procs[i].response_time);
    }

    double cpu_util = total_ticks > 0 ? ((double)busy_ticks / total_ticks) * 100.0 : 0.0;
    int context_switches = calculate_context_switches(gantt_timeline, total_ticks);
    
    printf("\\nRESULT: OK\\n");
    printf("ALG=%s\\n", alg);
    printf("AVG_WAIT=%.2f\\n", total_wait / n);
    printf("AVG_TAT=%.2f\\n", total_tat / n);
    printf("AVG_RESP=%.2f\\n", total_resp / n);
    printf("CONTEXT_SWITCHES=%d\\n", context_switches);
    printf("CPU_UTIL=%.2f%%\\n", cpu_util);
}
""",

    "src/algorithms.c": """#include <stdio.h>
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
        fprintf(stderr, "Error: Memory allocation failed\\n");
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
        fprintf(stderr, "Error: Memory allocation failed\\n");
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
        fprintf(stderr, "Error: Memory allocation failed\\n");
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
        fprintf(stderr, "Error: Memory allocation failed\\n");
        exit(1);
    }
    
    int current_time = 0;
    int completed_count = 0;

    int queue_capacity = n * 4;
    int* queue = (int*)malloc(queue_capacity * sizeof(int));
    int* in_queue = (int*)calloc(n, sizeof(int));
    
    if (!queue || !in_queue) {
        fprintf(stderr, "Error: Memory allocation failed\\n");
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
                    fprintf(stderr, "Warning: RR queue is full, process %s may be delayed\\n", procs[i].pid);
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
                fprintf(stderr, "Warning: RR queue is full, process %s may be delayed\\n", procs[running_idx].pid);
            }
            running_idx = -1;
        }
    }

    print_gantt_and_stats(procs, n, "RR", timeline, current_time);
    free(timeline);
    free(queue);
    free(in_queue);
}
""",

    "Makefile": """CC = gcc
CFLAGS = -Wall -Wextra -O2
SRC = src/main.c src/algorithms.c src/utils.c
OBJ = $(SRC:.c=.o)
TARGET = sched

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJ)

clean:
	rm -f $(OBJ) $(TARGET)
""",

    "README.md": """# CPU Scheduler Simulation (CPT104 Coursework 2)

## Context Switch 定义
本文档中，**context switch 的统计口径**如下：
- **计入 context switch**：进程A → 进程B（从执行一个进程切换到执行另一个进程）
- **不计入 context switch**：
  - 进程 → IDLE（进程执行完毕，CPU 空闲）
  - IDLE → 进程（CPU 从空闲状态开始执行新到达的进程）

这种口径符合常见调度模拟的惯例，且在下方各算法的实现中保持一致。

## 编译命令
```bash
make
```

## 运行方式
### Demo 模式
```bash
./sched --demo
```

### 正常运行模式
```bash
./sched workload.txt --alg FCFS
./sched workload.txt --alg SJF
./sched workload.txt --alg SRTF
./sched workload.txt --alg RR --q 3
```

## 支持的算法
- FCFS: First Come First Served
- SJF: Shortest Job First
- SRTF: Shortest Remaining Time First
- RR: Round Robin

## Workload 文件格式
```
P1 0 8
P2 1 4
P3 2 9
P4 3 5
```
格式：PID 到达时间 执行时间 [优先级]

注意：
- PID 最大长度为 15 个字符（超过会报错）
- 第4列（优先级）为可选字段，当前不参与调度
- 支持注释行（以 # 开头）
- **非法行会导致程序报错并以非零退出码终止**

## 输入错误处理
程序对非法输入的处理规则：
- **非法行会直接报错并退出（exit code != 0）**
- 错误类型包括但不限于：
  - 字段数量不足（少于3个）
  - 字段数量过多（多于4个）
  - PID 超过 15 个字符
  - PID 为空
  - 到达时间为负数
  - 执行时间非正数
  - 非数字字符（如 `1x`、`7abc`）

## 平局规则（Tie-Breaking）
当多个进程满足相同条件时，按以下顺序决定优先级：
1. 到达时间早的优先
2. 到达时间相同时，PID 字典序靠前的优先
""",

    "workload.txt": """P1 0 8
P2 1 4
P3 2 9
P4 3 5
"""
}

for directory in project_dirs:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

for filepath, content in files.items():
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        print(f"Created file: {filepath}")

print("\n✅ Project generation complete!")
