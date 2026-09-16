# Using yield to turn it into a generator that loads one line at a time into memory to process it and discard it, then streams the next line
# Keeps RAM usage around a flat 30MB-50MB regardlesss of log file size
def read_large_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            yield line

# It only compiles once to tell the CPU exactly how to layout search parameters in low-level memory to skip evaluating pattern string for each log line dynamically
log_pattern = re.compile(r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*?"\w+ \S+ \S+" (?P<status>\d{3})')

# Using hash map structure to inscrement for each hit on specific ip address for O(1) constant time complexity
for line in read_large_file(file_path):
    match = log_pattern.search(line)
    if match:
        ip_counter[match.group('ip')] += 1
