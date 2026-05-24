# CPU Scheduler Simulation (CPT104 Coursework 2)

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
