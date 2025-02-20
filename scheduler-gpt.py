#ChatGPT-Scheduler
#Spring 2025
# Group 41: Jack Livingston, Daniel Small, Carlos Martinez-Celedon, Michael Rivera

import sys
from collections import deque

class Process:
    def __init__(self, name, arrival, burst):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining_burst = burst
        self.start_time = -1
        self.completion_time = 0
        self.wait_time = 0
        self.turnaround_time = 0
        self.response_time = -1

def fcfs(processes, runfor):
    time = 0
    queue = sorted(processes, key=lambda p: p.arrival)
    output = []
    output.append(f"{len(processes)} processes")
    output.append("Using First-Come First-Served")
    
    for process in queue:
        while time < process.arrival:
            output.append(f"Time {time} : Idle")
            time += 1
        
        output.append(f"Time {time} : {process.name} arrived")
        output.append(f"Time {time} : {process.name} selected (burst {process.burst})")
        process.start_time = time
        process.wait_time = time - process.arrival
        time += process.burst
        process.completion_time = time
        process.turnaround_time = process.completion_time - process.arrival
        process.response_time = process.wait_time
        output.append(f"Time {time} : {process.name} finished")
    
    while time < runfor:
        output.append(f"Time {time} : Idle")
        time += 1
    output.append(f"Finished at time {runfor}")
    
    for process in sorted(queue, key=lambda p: p.name):
        output.append(f"{process.name} wait {process.wait_time} turnaround {process.turnaround_time} response {process.response_time}")
    
    return output

def rr(processes, runfor, quantum):
    time = 0
    queue = deque()
    processes.sort(key=lambda p: p.arrival)
    output = []
    output.append(f"{len(processes)} processes")
    output.append("Using Round-Robin")
    output.append(f"Quantum {quantum}")
    
    index = 0
    while time < runfor:
        while index < len(processes) and processes[index].arrival == time:
            queue.append(processes[index])
            output.append(f"Time {time} : {processes[index].name} arrived")
            index += 1
        
        if queue:
            process = queue.popleft()
            if process.response_time == -1:
                process.response_time = time - process.arrival
            output.append(f"Time {time} : {process.name} selected (burst {process.remaining_burst})")
            execute_time = min(quantum, process.remaining_burst)
            process.remaining_burst -= execute_time
            time += execute_time
            
            while index < len(processes) and processes[index].arrival < time:
                queue.append(processes[index])
                output.append(f"Time {processes[index].arrival} : {processes[index].name} arrived")
                index += 1
            
            if process.remaining_burst > 0:
                queue.append(process)
            else:
                process.completion_time = time
                process.turnaround_time = process.completion_time - process.arrival
                process.wait_time = process.turnaround_time - process.burst
                output.append(f"Time {time} : {process.name} finished")
        else:
            output.append(f"Time {time} : Idle")
            time += 1
    
    output.append(f"Finished at time {runfor}")
    for process in sorted(processes, key=lambda p: p.name):
        output.append(f"{process.name} wait {process.wait_time} turnaround {process.turnaround_time} response {process.response_time}")
    
    return output

def sjf(processes, runfor):
    time = 0
    queue = []
    output = []
    output.append(f"{len(processes)} processes")
    output.append("Using preemptive Shortest Job First")
    processes.sort(key=lambda p: (p.arrival, p.burst))
    index = 0
    
    while time < runfor:
        while index < len(processes) and processes[index].arrival == time:
            queue.append(processes[index])
            queue.sort(key=lambda p: p.remaining_burst)
            output.append(f"Time {time} : {processes[index].name} arrived")
            index += 1
        
        if queue:
            process = queue.pop(0)
            if process.response_time == -1:
                process.response_time = time - process.arrival
            output.append(f"Time {time} : {process.name} selected (burst {process.remaining_burst})")
            process.remaining_burst -= 1
            time += 1
            
            while index < len(processes) and processes[index].arrival == time:
                queue.append(processes[index])
                queue.sort(key=lambda p: p.remaining_burst)
                output.append(f"Time {time} : {processes[index].name} arrived")
                index += 1
            
            if process.remaining_burst > 0:
                queue.append(process)
                queue.sort(key=lambda p: p.remaining_burst)
            else:
                process.completion_time = time
                process.turnaround_time = process.completion_time - process.arrival
                process.wait_time = process.turnaround_time - process.burst
                output.append(f"Time {time} : {process.name} finished")
        else:
            output.append(f"Time {time} : Idle")
            time += 1
    
    output.append(f"Finished at time {runfor}")
    for process in sorted(processes, key=lambda p: p.name):
        output.append(f"{process.name} wait {process.wait_time} turnaround {process.turnaround_time} response {process.response_time}")
    
    return output

def main():
    if len(sys.argv) != 2:
        print("Usage: python scheduler.py <input_file>")
        return
    
    input_file = sys.argv[1]
    output_file = input_file.replace(".in", ".out")
    
    with open(input_file, "r") as f:
        lines = f.readlines()
    
    processes = []
    runfor = 0
    scheduler = ""
    quantum = 1
    
    for line in lines:
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "processcount":
            pass
        elif parts[0] == "runfor":
            runfor = int(parts[1])
        elif parts[0] == "use":
            scheduler = parts[1]
        elif parts[0] == "quantum":
            quantum = int(parts[1])
        elif parts[0] == "process":
            processes.append(Process(parts[2], int(parts[4]), int(parts[6])))
    
    if scheduler == "fcfs":
        result = fcfs(processes, runfor)
    elif scheduler == "rr":
        result = rr(processes, runfor, quantum)
    elif scheduler == "sjf":
        result = sjf(processes, runfor)
    
    with open(output_file, "w") as f:
        for line in result:
            f.write(line + "\n")

if __name__ == "__main__":
    main()
