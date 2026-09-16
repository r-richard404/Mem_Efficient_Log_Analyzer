import os
import re
import sys
import time
from collections import Counter
import json

# Using yield to turn it into a generator that loads one line at a time into memory to process it and discard it, then streams the next line
# Keeps RAM usage around a flat 30MB-50MB regardlesss of log file size
def read_large_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            yield line

# Main high-performance data processing function
def analyze_logs(file_path):
    print(f"[*] Starting analysis on: {file_path}")
    start_time = time.time()
    
    # Pre-compiled Regex pattern to optimize CPU cycles during search loops
    log_pattern = re.compile(r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*?"\w+ \S+ \S+" (?P<status>\d{3})')
    
    ip_counter = Counter()
    status_counter = Counter()
    total_lines = 0

    # Process line by line to maintain a footprint under 50MB RAM
    for line in read_large_file(file_path):
        total_lines += 1
        match = log_pattern.search(line)
        if match:
            data = match.groupdict()
            ip_counter[data['ip']] += 1
            status_counter[data['status']] += 1

    end_time = time.time()
    
    # Structure high level data output metrics
    results = {
        "metrics": {
            "total_lines_processed": total_lines,
            "execution_time_seconds": round(end_time - start_time, 4),
            "lines_per_second": int(total_lines / (end_time - start_time)) if (end_time - start_time) > 0 else total_lines
        },
        "top_active_ips": dict(ip_counter.most_common(5)),
        "http_status_distribution": dict(status_counter)
    }
    
    return results

# Automatically generates a mock dataset file of 100k lines for quick local testing
def generate_mock_logs(file_path, num_lines=100000):
    import random
    ips = [f"192.168.1.{random.randint(1, 254)}" for _ in range(20)] + ["10.0.0.5", "185.23.4.12"]
    statuses = ["200", "200", "200", "404", "500", "403"]
    
    with open(file_path, "w") as f:
        for _ in range(num_lines):
            f.write(f'{random.choice(ips)} - - [16/Sep/2026:00:12:00 +0000] "GET /api/v1/data HTTP/1.1" {random.choice(statuses)} 2326\n')

if __name__ == "__main__":
    mock_file = "server_access.log"
    
    if not os.path.exists(mock_file):
        print("[*] Generating mock server logs...")
        generate_mock_logs(mock_file, num_lines=100000)
        
    analysis_output = analyze_logs(mock_file)
    
    # Output metrics to a structured json file
    with open("log_metrics.json", "w") as json_file:
        json.dump(analysis_output, json_file, indent=4)
        
    print("\n[+] Analysis Complete! Metrics saved to log_metrics.json:")
    print(json.dumps(analysis_output, indent=4))
