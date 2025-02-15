import sys
import re

class Process:
    def __init__(self, name, arrival, burst):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining_time = burst
        self.start_time = -1
        self.finish_time = -1
        self.wait_time = 0
        self.turnaround_time = 0
        self.response_time = -1

def parse_input(filename):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    process_list = []
    algorithm = None
    quantum = None
    run_time = None
    process_count = None

    for line in lines:
        tokens = line.strip().split()
        if not tokens:
            continue

        if tokens[0] == "processcount":
            process_count = int(tokens[1])
        elif tokens[0] == "runfor":
            run_time = int(tokens[1])
        elif tokens[0] == "use":
            algorithm = tokens[1].lower()
        elif tokens[0] == "quantum":
            quantum = int(tokens[1])
        elif tokens[0] == "process":
            name = tokens[2]
            arrival = int(tokens[4])
            burst = int(tokens[6])
            process_list.append(Process(name, arrival, burst))
        elif tokens[0] == "end":
            break

    # Validation
    if process_count is None:
        print("Error: Missing parameter processcount.")
        sys.exit(1)
    if run_time is None:
        print("Error: Missing parameter runfor.")
        sys.exit(1)
    if algorithm is None:
        print("Error: Missing parameter use.")
        sys.exit(1)
    if algorithm == "rr" and quantum is None:
        print("Error: Missing quantum parameter when use is 'rr'")
        sys.exit(1)
    if len(process_list) != process_count:
        print("Error: Number of processes does not match processcount.")
        sys.exit(1)

    return process_list, algorithm, quantum, run_time, filename

def fcfs(processes, run_time):
    time = 0
    output = []
    processes.sort(key=lambda p: p.arrival)
    queue = []

    output.append(f"{len(processes)} processes")
    output.append("Using First-Come, First-Served")

    while time < run_time:
        for p in processes:
            if p.arrival == time:
                output.append(f"Time {time} : {p.name} arrived")
                queue.append(p)

        if queue:
            current = queue.pop(0)
            output.append(f"Time {time} : {current.name} selected (burst {current.burst})")
            current.response_time = time - current.arrival
            current.wait_time = current.response_time
            time += current.burst
            current.finish_time = time
            current.turnaround_time = current.finish_time - current.arrival
            output.append(f"Time {time} : {current.name} finished")
        else:
            output.append(f"Time {time} : Idle")
            time += 1

    output.append(f"Finished at time {run_time}")
    output.append("\n".join(format_results(processes)))
    return output

def sjf(processes, run_time):
    time = 0
    output = []
    queue = []
    processes.sort(key=lambda p: (p.arrival, p.burst))

    output.append(f"{len(processes)} processes")
    output.append("Using preemptive Shortest Job First")

    while time < run_time:
        for p in processes:
            if p.arrival == time:
                output.append(f"Time {time} : {p.name} arrived")
                queue.append(p)

        if queue:
            queue.sort(key=lambda p: (p.remaining_time, p.arrival))
            current = queue.pop(0)
            output.append(f"Time {time} : {current.name} selected (burst {current.remaining_time})")

            if current.response_time == -1:
                current.response_time = time - current.arrival

            current.remaining_time -= 1
            time += 1

            if current.remaining_time > 0:
                queue.append(current)
            else:
                current.finish_time = time
                output.append(f"Time {time} : {current.name} finished")

        else:
            output.append(f"Time {time} : Idle")
            time += 1

    output.append(f"Finished at time {run_time}")
    output.append("\n".join(format_results(processes)))
    return output

def round_robin(processes, run_time, quantum):
    time = 0
    output = []
    queue = []
    processes.sort(key=lambda p: p.arrival)
    index = 0

    output.append(f"{len(processes)} processes")
    output.append("Using Round-Robin")
    output.append(f"Quantum {quantum}")

    while time < run_time:
        while index < len(processes) and processes[index].arrival == time:
            queue.append(processes[index])
            output.append(f"Time {time} : {processes[index].name} arrived")
            index += 1

        if queue:
            current = queue.pop(0)
            output.append(f"Time {time} : {current.name} selected (burst {current.remaining_time})")

            if current.response_time == -1:
                current.response_time = time - current.arrival

            execute_time = min(quantum, current.remaining_time)
            current.remaining_time -= execute_time
            time += execute_time

            while index < len(processes) and processes[index].arrival <= time:
                queue.append(processes[index])
                output.append(f"Time {time} : {processes[index].name} arrived")
                index += 1

            if current.remaining_time > 0:
                queue.append(current)
            else:
                current.finish_time = time
                output.append(f"Time {time} : {current.name} finished")
        else:
            output.append(f"Time {time} : Idle")
            time += 1

    output.append(f"Finished at time {run_time}")
    output.append("\n".join(format_results(processes)))
    return output

def format_results(processes):
    results = []
    for p in sorted(processes, key=lambda p: p.name):
        turnaround = p.finish_time - p.arrival
        wait = turnaround - p.burst
        response = p.response_time
        results.append(f"{p.name} wait {wait} turnaround {turnaround} response {response}")
    return results

def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".in"):
        print("Usage: scheduler-gpt.py <input file>")
        sys.exit(1)

    processes, algorithm, quantum, run_time, filename = parse_input(sys.argv[1])
    output_filename = filename.replace(".in", ".out")

    if algorithm == "fcfs":
        output = fcfs(processes, run_time)
    elif algorithm == "sjf":
        output = sjf(processes, run_time)
    elif algorithm == "rr":
        output = round_robin(processes, run_time, quantum)

    with open(output_filename, "w") as f:
        f.write("\n".join(output) + "\n")

if __name__ == "__main__":
    main()
