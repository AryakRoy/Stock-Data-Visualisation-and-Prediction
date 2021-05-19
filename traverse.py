import os
import os.path
import time

path = os.walk("models")
model_files = []
for root, directories, files in path:
    model_files = files
times = {}
for file in model_files:
    path_ = os.path.join(os.getcwd(),"models",file)
    times[file] = os.path.getctime(path_)
oldest_time = min(times.values())
for file in times.keys():
    if times[file] == oldest_time:
        os.remove(os.path.join(os.getcwd(),"models",file))