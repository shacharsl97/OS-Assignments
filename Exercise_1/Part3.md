Mini Task Scheduler Implementation in C
=================================

Overview
--------
In this project, you will develop a **mini task scheduler** that executes commands based on a predefined schedule. Your program will read commands from a file, execute them at specified times, and log the results.

Requirements
------------

### 1. Reading Tasks from a File
Your program will take an input file (e.g., `tasks.txt`), where each line represents a command to be executed at a specific time with a priority. The format is:

```
<execution_time> <priority> <command>
```

- `<execution_time>`: Number of seconds to wait before executing the command.
- `<priority>`: An integer (lower number = higher priority) that determines execution order if multiple commands have the same execution time.
- `<command>`: The command to execute, including arguments.

Example `tasks.txt`:
```
5 1 ls -l
2 2 echo "Hello, World!"
10 1 sleep 3
```

### 2. Execution Order & Scheduling
- Commands should be sorted by **execution_time** (earliest first). If two commands have the same execution time, the one with **higher priority (lower number)** should run first.
- The program should wait the appropriate time (`execution_time` from program start) before running each command.
- Each command should run in its own child process (`fork()` and `exec()`).
- The program should wait for each command to finish (`wait()`) before running the next one.

### 3. Logging
- Create a log file (`scheduler.log`) to record executed commands with timestamps.
- Format each log entry as:
  ```
  [timestamp] Executed: <command>
  ```
- If a command fails, log an error message instead.

Example Run
------------

### Given `tasks.txt`:
```
2 2 echo "Task 1"
2 1 echo "Task 2"
5 1 ls -l
```

### Expected Execution Order:
1. Wait 2 seconds → Execute `echo "Task 2"`
2. Execute `echo "Task 1"`
3. Wait 3 more seconds (total 5) → Execute `ls -l`

Example scheduler.log:

[10:00:02] Executed: echo "Task 2"
[10:00:02] Executed: echo "Task 1"
[10:00:05] Executed: ls -l

Submission Requirements

Source code (scheduler.c or equivalent)

Compilation instructions in a README.md

Example input file (tasks.txt)

Example output (scheduler.log)

Good luck!