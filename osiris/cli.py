#!/usr/bin/env python3

import sys
import os
import datetime
import weather_data


# Ensure the script can find the todo module
sys.path.insert(0, os.path.dirname(__file__))
from todo import Task

def osiris():
    print("Hello Massimo,")
    
def today_weather():
    temp, weather = weather_data.get_today_weather()
    print(f"Temperature: {temp}°C, Weather:")

def add_task():
    Task.addTask()
    print("Task added successfully.")

def list_tasks():
    tasks = Task.initTasks()
    Task.showTasks(tasks)

def place_tasks():
    tasks = Task.initTasks()
    Task.tasksInCal(tasks)
    print('tasks placed in calendar successfully')

def remove_task():
    tasks = Task.initTasks()
    for task in tasks:
        print(task.task)
    removed_task = input('Input exact name of task: ')
    for task in tasks:
        if task.task == removed_task:
            Task.removeTask(task)

# Command Mapping
commands = {
    "gm" : osiris,

    "at": add_task,
    "rt": remove_task,
    "lt": list_tasks,
    "pt": place_tasks,

    "tw": today_weather
}

def main():
    if len(sys.argv) < 2:
        print("Usage: osiris [command]")  # Help message
        sys.exit(1)

    command = sys.argv[1].lower()

    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: addtask, removetask, listtasks, placetasks")

if __name__ == "__main__":
    main()
