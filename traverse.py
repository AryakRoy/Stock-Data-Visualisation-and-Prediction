import os
import os.path
import time
from datetime import datetime

class Traverse:
    def __init__(self):
        self.path = os.walk("models")
        self.model_files = []
        self.init_files()
        self.limit = 10
    
    def init_files(self):
        for root, directories, files in self.path:
            self.model_files = files
    
    def is_file_in_directory(self,ticker):
        self.init_files()
        if f"{ticker}.h5" in self.model_files:
            return True
        else:
            return False

    def remove_files(self):
        times = {}
        for file in self.model_files:
            path_ = os.path.join(os.getcwd(),"models",file)
            times[file] = os.path.getctime(path_)
        oldest_time = min(times.values())
        for file in times.keys():
            if times[file] == oldest_time:
                os.remove(os.path.join(os.getcwd(),"models",file))
                break

    def traverse(self,ticker):
        self.init_files()
        if self.is_file_in_directory(ticker):
            path_ = os.path.join(os.getcwd(),"models",f"{ticker}.h5")
            file_time = os.path.getctime(path_)
            file_time = int(datetime.fromtimestamp(file_time).strftime('%d'))
            now_time = int(datetime.now().strftime("%d"))
            if file_time < now_time:
                os.remove(os.path.join(os.getcwd(),"models",f"{ticker}.h5"))
        else:
            if len(self.model_files) < self.limit:
                return
            else:
                self.remove_files()