#!/usr/bin/env python3

# 简单的算法逻辑验证脚本
# 用于验证我们的调度算法逻辑是否正确

class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid
        self.arrival_time = arrival
        self.burst_time = burst
        self.remaining_time = burst
        self.start_time = -1
        self.end_time = 0
        self.wait_time = 0
        self.turnaround_time = 0
        self.response_time = 0
        self.is_completed = False
        self.first_run = True


def test_fcfs():
    print("=== 测试FCFS算法 ===")
    procs = [
        Process("P1", 0, 8),
        Process("P2", 1, 4),
        Process("P3", 2, 9),
        Process("P4", 3, 5)
    ]
    
    # 按到达时间排序
    procs.sort(key=lambda p: (p.arrival_time, p.pid))
    
    current_time = 0
    timeline = []
    
    for p in procs:
        while current_time < p.arrival_time:
            timeline.append(-1)
            current_time += 1
        
        p.start_time = current_time
        p.response_time = p.start_time - p.arrival_time
        
        for _ in range(p.burst_time):
            timeline.append(procs.index(p))
            current_time += 1
        
        p.end_time = current_time
        p.turnaround_time = p.end_time - p.arrival_time
        p.wait_time = p.turnaround_time - p.burst_time
        p.is_completed = True
    
    print("甘特图:", " ".join(["IDLE" if x == -1 else procs[x].pid for x in timeline]))
    print("结果:")
    for p in procs:
        print(f"{p.pid}: 等待时间={p.wait_time}, 周转时间={p.turnaround_time}")
    
    # 验证上下文切换
    switches = 0
    last_pid = -1
    for pid in timeline:
        if last_pid != -1 and pid != -1 and last_pid != pid:
            switches += 1
        last_pid = pid
    print(f"上下文切换次数: {switches}")
    print()


def test_input_validation():
    print("=== 测试输入校验逻辑 ===")
    test_cases = [
        ("正常输入", "P1 0 5", True),
        ("负数到达时间", "P1 -1 5", False),
        ("零执行时间", "P1 0 0", False),
        ("负数执行时间", "P1 0 -5", False),
        ("空PID", "  0 5", False),
    ]
    
    for name, line, should_pass in test_cases:
        parts = line.strip().split()
        result = True
        if len(parts) < 3:
            result = False
        else:
            pid = parts[0]
            arrival = int(parts[1])
            burst = int(parts[2])
            if len(pid) == 0:
                result = False
            if arrival < 0:
                result = False
            if burst <= 0:
                result = False
        
        status = "✓ PASS" if result == should_pass else "✗ FAIL"
        print(f"{status}: {name} - '{line}'")
    
    print()


if __name__ == "__main__":
    print("CPU调度算法验证脚本")
    print("=" * 40)
    print()
    
    test_fcfs()
    test_input_validation()
    
    print("验证完成！")
    print("\n注意: 这只是一个简单的逻辑验证脚本")
    print("完整的C程序编译需要GCC编译器")
