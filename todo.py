import heapq
import osiris_cal
import datetime
from datetime import timedelta, datetime
from random import randint
import pandas
import csv

class Task:
    ''' 
    def __init__(self,tasks_list):
        self.tasks_list = tasks_list
    '''
    def __init__(self, task:str, priority:int, duration:int, due_date:datetime, declaration_date=None, active=False):        
        self.task = task # Description
        self.priority = priority # Integer with range [1,10]
        self.duration = duration # Integer time in hours
        self.due_date = due_date
        self.declaration_date = (datetime.today() if not declaration_date else declaration_date)  # Date of creation of task as datetime object
        self.active = (False if not active else active)
        


    def showTasks(todo_list:list) -> None:
        task:Task
        for task in todo_list:
            print(f"task:{task.task} priority:{task.priority} expected time:{task.duration} due date:{task.due_date} declaration date:{datetime.strftime(task.declaration_date,"%d/%m/%Y %H:%M:%S")} active:{task.active}")
    
    def sortTasks(tasks_list:list) -> list:
        return sorted(tasks_list, key= lambda x: (-x.priority, x.duration))
    
    def tasksInCal(tasks_list:list) -> None:
        task:Task

        sorted_tasks = Task.sortTasks(tasks_list)
        
        for task in sorted_tasks:

            occupied_slots_UOE = osiris_cal.get_calendar_events(datetime.today(), task.due_date, "UOE")
            occupied_slots_osiris = osiris_cal.get_calendar_events(datetime.today(), task.due_date, "osiris")
            occupied_slots = occupied_slots_UOE + occupied_slots_osiris

            time_slots = osiris_cal.getFreeSlots(task.due_date,occupied_slots)
            for time_slot in time_slots:
                slot_timedelta = time_slot[1] - time_slot[0]
                slot_timedelta = int(slot_timedelta.total_seconds()/3600)
                if slot_timedelta >= task.duration:
                    event_start = time_slot[0]
                    event_end = time_slot[0]+timedelta(hours=task.duration)
                    osiris_cal.add_calendar_event(event_start,event_end,task.task)
                    task.active = True
                    break
            if task.active == False:
                print(f'\ntask: {task.task} | task timedelta: {task.duration} | slot search range: {(datetime.today(), task.due_date)} --> placement unsuccessful')

    def initTasks(csvfile='tasks.csv') -> list[object]:
        Tasks = list()
        with open(csvfile,'r',newline='') as file:
            reader = csv.DictReader(file)
            for task in reader: # Task represents rows
                Tasks.append(Task(
                    task['task'],
                    int(task['priority']),
                    float(task['duration']),
                    datetime.strptime(task['due_date'], f"%d/%m/%Y %H:%M:%S"),
                    datetime.strptime(task['declaration_date'], f"%d/%m/%Y %H:%M:%S")
                    ))
        return Tasks

    def addTask(csvfile='tasks.csv') -> None:

        # Get task description
        task = input('Task description: ')

        # Get task priority
        while True:
            priority = input('Priority level (1,10): ')
            try:
                priority = int(priority)
                break
            except ValueError:
                print('Task priority must be of type int')

        # Get task duration
        while True:
            duration = input('Task duration (hr): ')
            try:
                duration = float(duration)
                break
            except ValueError:
                print('Task duration must be numeric string')

        # Get due date
        while True:
            due_date = input('Task due date (d/m/Y H:M:S): ')
            try:
                datetime.strptime(due_date, f"%d/%m/%Y %H:%M:%S")
                break
            except ValueError:
                print("task due date must be of format d/m/Y H:M:S (i.e. 10/05/2004 13:30:00)")

        # Get declaration date
        declaration_date = datetime.strftime(datetime.today().replace(microsecond=0), f"%d/%m/%Y %H:%M:%S")

        row = [task,priority,duration,due_date,declaration_date]
        with open(csvfile,'a',newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)       

    def removeTask(csvfile,task) -> None:
        task_row = [task.task, task.priority, task.duration, task.due_date, task.declaration_date]
        with open(csvfile,'r',newline='') as file:
            reader = csv.reader(file)
            rows = [row for row in reader if row != task_row]
        
        with open(csvfile,'w') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

if __name__ == '__main__':

    print()

    todo_list = list()
    # Initiate test set
    for i in range(20):
        todo_list.append(Task(
                task=f"test_task{i}", 
                priority=randint(1,10), 
                duration=randint(1,5), 
                due_date=datetime.today()+timedelta(days=randint(2,10))
                ))
    # print("\nTasks:")
    # Task.showTasks(todo_list)
    # print("\nSorted Tasks:")
    # Task.showTasks(Task.sortTasks(todo_list))
    # print("\nAdd tasks to cal")
    # Task.tasksInCal(todo_list)
    tasks = Task.initTasks()
    for task in tasks:
        print(f'{task.task}')
    # Task.addTask()
    print("\nDone")

    print()