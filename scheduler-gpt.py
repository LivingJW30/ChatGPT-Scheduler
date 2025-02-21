#ChatGPT-Scheduler
#Spring 2025
# Group 41: Jack Livingston, Daniel Small, Carlos Martinez-Celedon, Michael Rivera, and Rayyan Vorajee

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
    
    index = 0  # Track which process arrives next
    ready_queue = []
    current_process = None
    
    while time < runfor:
        # Announce arrivals at the correct time
        while index < len(queue) and queue[index].arrival == time:
            output.append(f"Time {time} : {queue[index].name} arrived")
            ready_queue.append(queue[index])
            index += 1
        
        if current_process is None and ready_queue:
            current_process = ready_queue.pop(0)
            output.append(f"Time {time} : {current_process.name} selected (burst {current_process.burst})")
            current_process.start_time = time
            current_process.wait_time = time - current_process.arrival
            current_process.response_time = current_process.wait_time
            current_process.remaining_burst = current_process.burst
        
        if current_process:
            current_process.remaining_burst -= 1
            if current_process.remaining_burst == 0:
                current_process.completion_time = time + 1
                current_process.turnaround_time = current_process.completion_time - current_process.arrival
                output.append(f"Time {time + 1} : {current_process.name} finished")
                current_process = None
        else:
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
    remaining_burst = {p.name: p.burst for p in processes}
    completion_time = {}
    first_execution = {}
    last_execution_time = {}
    total_wait_time = {p.name: 0 for p in processes}  # Corrected wait time tracking

    while time < runfor:
        # Add new arrivals to the queue
        while index < len(processes) and processes[index].arrival <= time:
            queue.append(processes[index])
            output.append(f"Time {processes[index].arrival:3} : {processes[index].name} arrived")
            index += 1
        
        if queue:
            process = queue.popleft()

            if process.name not in first_execution:
                first_execution[process.name] = time  # Set response time only for first execution

            output.append(f"Time {time:3} : {process.name} selected (burst {remaining_burst[process.name]})")

            execute_time = min(quantum, remaining_burst[process.name])
            remaining_burst[process.name] -= execute_time

            # Wait time = total time spent waiting in the queue before execution
            if process.name in last_execution_time:
                total_wait_time[process.name] += (time - last_execution_time[process.name])

            time += execute_time
            last_execution_time[process.name] = time  # Update last execution time

            # Check for new arrivals while process was running
            while index < len(processes) and processes[index].arrival <= time:
                queue.append(processes[index])
                output.append(f"Time {processes[index].arrival:3} : {processes[index].name} arrived")
                index += 1

            if remaining_burst[process.name] > 0:
                queue.append(process)  # Process still has remaining burst time
            else:
                completion_time[process.name] = time  # Process finished
                output.append(f"Time {time:3} : {process.name} finished")
        else:
            output.append(f"Time {time:3} : Idle")
            time += 1

    output.append(f"Finished at time {runfor}")

    # Compute turnaround, wait, and response times
    results = []
    for process in sorted(processes, key=lambda p: p.name):
        turnaround = completion_time[process.name] - process.arrival
        response = first_execution[process.name] - process.arrival
        wait = turnaround - process.burst  # Corrected wait time

        results.append(f"{process.name} wait {wait:3} turnaround {turnaround:3} response {response:3}")

    output.extend(results)
    return output

def sjf(processes, runfor):
    time = 0
    queue = []
    output = []
    output.append(f"{len(processes)} processes")
    output.append("Using preemptive Shortest Job First")
    processes.sort(key=lambda p: (p.arrival, p.burst))
    index = 0
    current_process = None
    
    while time < runfor:
        # Announce arrivals at the correct time
        while index < len(processes) and processes[index].arrival == time:
            queue.append(processes[index])
            queue.sort(key=lambda p: p.remaining_burst)
            output.append(f"Time {time} : {processes[index].name} arrived")
            index += 1
        
        # Select the process with the shortest remaining burst
        if queue and (current_process is None or current_process.remaining_burst > queue[0].remaining_burst):
            if current_process and current_process.remaining_burst > 0:
                queue.append(current_process)
                queue.sort(key=lambda p: p.remaining_burst)
            current_process = queue.pop(0)
            output.append(f"Time {time} : {current_process.name} selected (burst {current_process.remaining_burst})")
            if current_process.response_time == -1:
                current_process.response_time = time - current_process.arrival
        
        if current_process:
            # Process execution
            current_process.remaining_burst -= 1
            if current_process.remaining_burst == 0:
                current_process.completion_time = time + 1
                current_process.turnaround_time = current_process.completion_time - current_process.arrival
                current_process.wait_time = current_process.turnaround_time - current_process.burst
                output.append(f"Time {time + 1} : {current_process.name} finished")
                current_process = None  # Process completed
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
