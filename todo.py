import heapq
import datetime


class task:
    def __init__(self, exp_time:int, task:str, priority:int, by=None):
        
        self.task = task
        self.priority = priority
        self.time = exp_time # In minutes
        
        if by == None:
            self.by = datetime.date.strftime(datetime.date.today() + datetime.timedelta(days=7), "%d/%m/%Y %H:%M:%S")
        else:
            self.by = by
            
        

    def __lt__(self,other):
        return self.priority < other.priority
        pass