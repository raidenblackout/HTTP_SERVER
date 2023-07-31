import time
from threading import Thread
from queue import PriorityQueue
class Logger:
    def __init__(self, log_file):
        self.log_file = log_file
        self.status = 'idle'
        self.log_queue = PriorityQueue()
        self.log_thread = Thread(target=self.start)
        self.log_thread.start()
        self.log_queue.put((time.time(), "Logger started", "INFO",'SYSTEM'))
    
    #puts a log message in the queue
    def log(self, message, ip='SYSTEM', type = 'INFO'):
        self.log_queue.put((time.time(), message, type,ip))
    
    #starts the logger
    def start(self):
        while self.status != 'stopped' or self.log_queue.empty() == False:
            if self.log_queue.empty() == False:
                log = self.log_queue.get()
                curr_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(log[0]))
                with open(self.log_file, 'a') as f:
                    for line in log[1].split('\n'):
                        line = line.strip()
                        if line =='':
                            continue
                        #format [date time stamp] [type] [ip]: [message]
                        f.write(f"[{curr_time}] [{log[2]}] [{log[3]}]: {line}\n")
            time.sleep(0.1)

    #stops the logger
    def stop(self):
        self.log_queue.put((time.time(), "Logger stopped", "INFO",'SYSTEM'))
        self.status = 'stopped'
        self.log_thread.join()

    