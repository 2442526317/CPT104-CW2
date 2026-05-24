# 测试指南

## 环境要求
- GCC编译器（Windows上可以安装MinGW或使用WSL）
- Make工具

## 编译项目
```bash
# 在项目根目录下
make
```

如果没有make，可以直接用gcc编译：
```bash
gcc -Wall -Wextra -O2 -o sched.exe src/main.c src/algorithms.c src/utils.c
```

## 测试命令

### 1. 测试Demo模式
```bash
./sched --demo
```

### 2. 测试FCFS算法
```bash
./sched workload.txt --alg FCFS
```

### 3. 测试SJF算法
```bash
./sched workload.txt --alg SJF
```

### 4. 测试SRTF算法
```bash
./sched workload.txt --alg SRTF
```

### 5. 测试RR算法（使用--q参数）
```bash
./sched workload.txt --alg RR --q 3
```

## 验证点

1. **上下文切换计算**：检查是否只在进程A→进程B时计数
2. **输入校验**：尝试输入负数arrival_time或非正数burst_time，应该报错退出
3. **RR队列**：应该不会出现越界问题
4. **PID缓冲区**：输入超过15个字符的PID，应该被安全截断

## 在Windows上安装编译器

### 选项1：MinGW-w64
1. 下载MSYS2: https://www.msys2.org/
2. 安装后在MSYS2终端运行：
   ```bash
   pacman -S mingw-w64-x86_64-gcc make
   ```
3. 将 `C:\msys64\mingw64\bin` 添加到系统PATH

### 选项2：WSL (推荐)
1. 在Windows功能中启用WSL
2. 安装Ubuntu
3. 在Ubuntu中安装gcc和make：
   ```bash
   sudo apt update
   sudo apt install gcc make
   ```
