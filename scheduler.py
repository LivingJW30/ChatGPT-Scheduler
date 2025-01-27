#!/usr/bin/env python3

import sys
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Process:
    name: str
    arrival: int
    burst: int
    remaining_time: int
    start_time: Optional[int] = None
    finish_time: Optional[int] = None
    
    @property
    def response_time(self) -> int:
        return self.start_time - self.arrival if self.start_time is not None else 0
    
    @property
    def turnaround_time(self) -> int:
        return self.finish_time - self.arrival if self.finish_time is not None else 0
    
    @property
    def wait_time(self) -> int:
        return self.turnaround_time - self.burst if self.finish_time is not None else 0

class Scheduler:
    def __init__(self):
        self.processes: List[Process] = []
        self.total_time = 0
        self.algorithm = ""
        self.quantum = 0
        self.current_time = 0
        self.output_lines = []
        
    def parse_input(self, filename: str) -> None:
        try:
            with open(filename, 'r') as f:
                lines = [line.split('#')[0].strip() for line in f.readlines()]
                lines = [line for line in lines if line]
                
            i = 0
            while i < len(lines):
                parts = lines[i].split()
                if parts[0] == 'processcount':
                    process_count = int(parts[1])
                elif parts[0] == 'runfor':
                    self.total_time = int(parts[1])
                elif parts[0] == 'use':
                    self.algorithm = parts[1]
                elif parts[0] == 'quantum':
                    if self.algorithm != 'rr':
                        raise ValueError("Quantum specified but not using Round Robin")
                    self.quantum = int(parts[1])
                elif parts[0] == 'process':
                    name = parts[2]
                    arrival = int(parts[4])
                    burst = int(parts[6])
                    process = Process(name, arrival, burst, burst)
                    self.processes.append(process)
                i += 1

            if self.algorithm == 'rr' and self.quantum == 0:
                raise ValueError("Error: Missing quantum parameter when use is 'rr'")
                
        except FileNotFoundError:
            print(f"Error: Could not open input file '{filename}'")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)

    def log_event(self, message: str) -> None:
        self.output_lines.append(f"Time {self.current_time:3d} : {message}")

    def run_fcfs(self) -> None:
        self.log_event(f"{len(self.processes)} processes")
        self.log_event("Using First-Come First-Served")
        
        unfinished = self.processes.copy()
        current_process = None
        
        while self.current_time < self.total_time:
            # Check for newly arrived processes
            for process in unfinished:
                if process.arrival == self.current_time:
                    self.log_event(f"{process.name} arrived")
            
            # If no process is running, select the first arrived unfinished process
            if current_process is None:
                ready_processes = [p for p in unfinished if p.arrival <= self.current_time]
                if ready_processes:
                    current_process = min(ready_processes, key=lambda p: p.arrival)
                    if current_process.start_time is None:
                        current_process.start_time = self.current_time
                    self.log_event(f"{current_process.name} selected (burst {current_process.remaining_time:3d})")
                else:
                    self.log_event("Idle")
            
            # Process execution
            if current_process:
                current_process.remaining_time -= 1
                if current_process.remaining_time == 0:
                    current_process.finish_time = self.current_time + 1
                    self.log_event(f"{current_process.name} finished")
                    unfinished.remove(current_process)
                    current_process = None
            
            self.current_time += 1
            
        self.log_event(f"Finished at time {self.current_time}")

    def run_sjf(self) -> None:
        self.log_event(f"{len(self.processes)} processes")
        self.log_event("Using preemptive Shortest Job First")
        
        unfinished = self.processes.copy()
        current_process = None
        
        while self.current_time < self.total_time:
            # Check for newly arrived processes
            for process in unfinished:
                if process.arrival == self.current_time:
                    self.log_event(f"{process.name} arrived")
                    # Preempt if new process has shorter remaining time
                    if current_process and process.remaining_time < current_process.remaining_time:
                        current_process = None
            
            # Select process with shortest remaining time
            ready_processes = [p for p in unfinished if p.arrival <= self.current_time]
            if ready_processes:
                shortest_process = min(ready_processes, key=lambda p: p.remaining_time)
                if current_process != shortest_process:
                    current_process = shortest_process
                    if current_process.start_time is None:
                        current_process.start_time = self.current_time
                    self.log_event(f"{current_process.name} selected (burst {current_process.remaining_time:3d})")
            else:
                self.log_event("Idle")
                current_process = None
            
            # Process execution
            if current_process:
                current_process.remaining_time -= 1
                if current_process.remaining_time == 0:
                    current_process.finish_time = self.current_time + 1
                    self.log_event(f"{current_process.name} finished")
                    unfinished.remove(current_process)
                    current_process = None
            
            self.current_time += 1
            
        self.log_event(f"Finished at time {self.current_time}")

    def run_rr(self) -> None:
        self.log_event(f"{len(self.processes)} processes")
        self.log_event("Using Round-Robin")
        self.log_event(f"Quantum {self.quantum:3d}")
        
        unfinished = self.processes.copy()
        current_process = None
        quantum_remaining = self.quantum
        
        while self.current_time < self.total_time:
            # Check for newly arrived processes
            for process in unfinished:
                if process.arrival == self.current_time:
                    self.log_event(f"{process.name} arrived")
            
            # If no process is running or quantum expired, select next process
            if current_process is None or quantum_remaining == 0:
                ready_processes = [p for p in unfinished if p.arrival <= self.current_time]
                if ready_processes:
                    # If current process still has work, add it to the end of ready queue
                    if current_process and current_process.remaining_time > 0:
                        ready_processes.append(ready_processes.pop(0))
                    
                    current_process = ready_processes[0]
                    quantum_remaining = self.quantum
                    if current_process.start_time is None:
                        current_process.start_time = self.current_time
                    self.log_event(f"{current_process.name} selected (burst {current_process.remaining_time:3d})")
                else:
                    self.log_event("Idle")
                    current_process = None
            
            # Process execution
            if current_process:
                current_process.remaining_time -= 1
                quantum_remaining -= 1
                if current_process.remaining_time == 0:
                    current_process.finish_time = self.current_time + 1
                    self.log_event(f"{current_process.name} finished")
                    unfinished.remove(current_process)
                    current_process = None
                    quantum_remaining = 0
            
            self.current_time += 1
            
        self.log_event(f"Finished at time {self.current_time}")

    def print_statistics(self) -> None:
        self.output_lines.append("")  # Empty line before statistics
        unfinished_processes = [p for p in self.processes if p.finish_time is None]
        finished_processes = [p for p in self.processes if p.finish_time is not None]
        
        # Print unfinished processes first
        for process in unfinished_processes:
            self.output_lines.append(f"{process.name} did not finish")
            
        # Print statistics for finished processes
        for process in finished_processes:
            self.output_lines.append(
                f"{process.name} wait {process.wait_time:3d} "
                f"turnaround {process.turnaround_time:3d} "
                f"response {process.response_time:3d}"
            )

    def run(self) -> None:
        if self.algorithm == 'fcfs':
            self.run_fcfs()
        elif self.algorithm == 'sjf':
            self.run_sjf()
        elif self.algorithm == 'rr':
            self.run_rr()
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
            
        self.print_statistics()

    def write_output(self, input_filename: str) -> None:
        output_filename = input_filename.replace('.in', '.out')
        try:
            with open(output_filename, 'w') as f:
                for line in self.output_lines:
                    f.write(line + '\n')
        except Exception as e:
            print(f"Error writing output file: {str(e)}")
            sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: scheduler-gpt.py <input file>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    if not input_file.endswith('.in'):
        print("Error: Input file must have .in extension")
        sys.exit(1)
        
    scheduler = Scheduler()
    scheduler.parse_input(input_file)
    scheduler.run()
    scheduler.write_output(input_file)

if __name__ == "__main__":
    main()
