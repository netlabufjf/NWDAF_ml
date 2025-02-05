import os
import time

from joblib import Parallel, delayed
from pcap_json2csv.json2csv import parse

start_time = time.time() # record the start of execution
number_of_parallel_jobs=int(os.cpu_count()/2) # take half of reported CPU threads
# File paths
input_files_path = "./pcap/output/1-PCAP-export/" # read JSON files from here
output_files_path = "./pcap/output/3-JSON-export/" # save the output there

# get the list of all JSON files in the input directory
input_files_names = [f for f in os.listdir(input_files_path) if f.endswith('.json')]
# input_files_names = [f for f in os.listdir(input_files_path) if f.endswith('test.json') | f.endswith('5g1.json')] # initial tests
# create a list of file paths by joining the input directory path with each file name
input_file_paths = [os.path.join(input_files_path, f) for f in input_files_names]

# check if at least one file was found
if not input_file_paths:
    print(f"[ERRO] No JSON file found on {input_files_path}")
    exit()

# parse all JSON files read
def export_json(file, progress_bar_slow_print):
    try:
        parse(file, output_files_path, progress_bar_slow_print)
    except KeyboardInterrupt:
        print("\n[ERRO] Operation interrupted by the user")
        exit()
    print(f"\n[INFO] Export of {file} done")

try:
    slowdown_print=True
    print(f"[INFO] Running in parallel using {number_of_parallel_jobs} threads")
    Parallel(n_jobs=number_of_parallel_jobs)(delayed(export_json)(i, slowdown_print) for i in input_file_paths)
except KeyboardInterrupt:
    print("[ERRO] User asked to quit")
    exit()
# swap the lines on the block above with these below to disable the parallel execution
# for i in input_file_paths:
#     slowdown_print=False
#     export_json(i, slowdown_print)
end_time = time.time() # record the end of execution
print("Execution time:", end_time - start_time, "s") # TODO save this on disk
