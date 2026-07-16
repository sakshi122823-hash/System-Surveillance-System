System Surveillance System

A Python command-line tool  that periodically scans your system (CPU, RAM, disk, network, and per-process stats) and writes the results to a timestamped log file, then emails a summary report with the log attached.

Features


Process Scan — PID, name, username, status, create time, CPU %, memory %
Thread Monitoring — thread count per running process
Open Files Monitoring — count of open file descriptors per process
Memory Allocation — RSS (actual RAM) and VMS (virtual memory) per process, plus a Top 10 by memory usage
System Usage — overall CPU %, RAM %, disk usage per partition, network bytes sent/received
Automatic Logging — writes everything to a timestamped .log file in a directory you choose
Scheduled Execution — runs automatically every N minutes using the schedule library
Email Reports — sends a summary email (Top 5 CPU/Memory/Thread/Open-Files processes) with the full log file attached via Gmail SMTP


Requirements


Python 3
Dependencies:


bash  pip install psutil schedule

(smtplib, email, sys, os, time are part of the Python standard library.)
