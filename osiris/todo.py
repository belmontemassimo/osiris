
import osiris_cal
from datetime import timedelta, datetime, time
import csv

class Task:
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
            print(f"task: {task.task} priority: {task.priority} expected time: {task.duration} "
                  f"due date: {task.due_date} declaration date: {task.declaration_date.strftime('%d/%m/%Y %H:%M:%S')} active: {task.active}")
 
    def sortTasks(tasks_list:list) -> list:
        return sorted(tasks_list, key= lambda x: (-x.priority, x.duration))
    
    def tasksInCal(tasks_list:list) -> None:

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
                    task.removeTask()
                    task.active = True
                    break

            if not task.active:
                print(f'\ntask: {task.task} | task timedelta: {task.duration} | slot search range: {(datetime.today(), task.due_date)} --> placement unsuccessful')
            
        tasks = Task.initTasks()
        if len(tasks) > 0:
            Task.splitTasks(tasks)
            Task.tasksInCal(Task.initTasks())

    def initTasks(csvfile='/Users/massimobelmonte/Desktop/GIT-Projects/osiris/osiris data/tasks.csv') -> list[object]:
        Tasks = list()
        
        with open(csvfile,'r') as file:
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

    def splitTasks(tasks_list:list) -> None:
        atask:Task
        seen_tasks = set()
        for atask in tasks_list:
            if atask.task in seen_tasks:
                continue
            else:
                seen_tasks.add(atask.task)

            atask.removeTask()
            parts_count = 0

            for title in tasks_list:
                title = title.task
                if title == atask.task:
                    parts_count += 1

            for i in range(2 * parts_count):
                Task.addTask(task=atask.task,
                            priority=atask.priority,
                            duration=atask.duration/2,
                            due_date=atask.due_date,
                            declaration_date=atask.declaration_date)
            
    def addTask(csvfile='/Users/massimobelmonte/Desktop/GIT-Projects/osiris/osiris data/tasks.csv', **kwargs) -> None:

        task = kwargs.get('task')
        priority = kwargs.get('priority')
        duration = kwargs.get('duration')
        due_date = kwargs.get('due_date')
        declaration_date = datetime.strftime(kwargs.get('declaration_date',datetime.today()), f"%d/%m/%Y %H:%M:%S")


        if not task:
            # Get task description
            task = input('Task description: ')

        if not priority:
            # Get task priority
            while True:
                priority = input('Priority level (1,10): ')
                try:
                    priority = int(priority)
                    break
                except ValueError:
                    print('Task priority must be of type int')
        else:
            priority = int(priority)

        if not duration:
            # Get task duration
            while True:
                duration = input('Task duration (hr): ')
                try:
                    duration = float(duration)
                    break
                except ValueError:
                    print('Task duration must be numeric string')
        else:
            duration = float(duration)

        if not due_date:
            # Get due date
            while True:
                due_date = input('Task due date (d/m/Y H:M:S): ')
                try:
                    datetime.strptime(due_date, f"%d/%m/%Y %H:%M:%S")
                    break
                except ValueError:
                    print("task due date must be of format d/m/Y H:M:S (i.e. 10/05/2004 13:30:00)")
        else:
            due_date = datetime.strftime(due_date, f"%d/%m/%Y %H:%M:%S")

        


        row = [task,priority,duration,due_date,declaration_date]

        with open(csvfile,'a') as file:
            writer = csv.writer(file)
            writer.writerow(row)       

    def removeTask(self,csvfile='/Users/massimobelmonte/Desktop/GIT-Projects/osiris/osiris data/tasks.csv') -> None:

        task_row = [self.task, 
                    str(self.priority), 
                    str(self.duration), 
                    datetime.strftime(self.due_date,f"%d/%m/%Y %H:%M:%S"), 
                    datetime.strftime(self.declaration_date,f"%d/%m/%Y %H:%M:%S")]

        with open(csvfile,'r') as file:
            reader = csv.reader(file)
            rows = [row for row in reader if row != task_row]
                
        with open(csvfile,'w') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

    def dayTasks(days=0):
        delta = timedelta(days=days)

        tasks = osiris_cal.get_calendar_events(datetime.combine(datetime.today().date()+delta, time(0,0,0)),datetime.combine(datetime.today().date()+delta, time(23,59,59)),calendar="UOE")
        tasks += osiris_cal.get_calendar_events(datetime.combine(datetime.today().date()+delta, time(0,0,0)),datetime.combine(datetime.today().date()+delta, time(23,59,59)),calendar="osiris")
        
        print(f"\n\033[1mList of events on {datetime.strftime(datetime.today() + delta, '%A %-d %B')}:\033[0m\n")        
        
        current_time = datetime.now()
        for task in tasks:

            start_time = task[1]
            end_time = task[2]

            if end_time < current_time:
                # print(f"{task[0]}:")
                # print(f"{start_time} < {end_time} < {current_time}\n")
                status = '\033[1mexpired\033[0m'

            elif start_time <= current_time and end_time > current_time:
                # print(f"{task[0]}:")
                # print(f"\n")
                status = '\033[1mongoing\033[0m'

            elif start_time > current_time:
                status = '\033[1mupcoming\033[0m'
            
            print(f"{datetime.strftime(task[1],f'%H:%M:%S')} -> {datetime.strftime(task[2],f'%H:%M:%S')}: {status}")
            print(f"{task[0]}\n")



if __name__ == '__main__':
    # Task init test:
    tasks = Task.initTasks()

    # # Task removal test:
    # Task.removeTask(tasks[-1])

    # # Task adding test:
    # Task.addTask(task='test_task_11',priority=1,duration=3.0,due_date=datetime.today()+timedelta(days=1))

    # Task in cal test:
    Task.tasksInCal(tasks)
    
    