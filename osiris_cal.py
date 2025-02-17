import subprocess
import datetime
from datetime import datetime, timedelta, time

def get_calendar_events(start_date:datetime, end_date:datetime, calendar="UOE") -> list[tuple[str,datetime,datetime]]:
    # Get data from calendar app through apple script

    start_date_str = datetime.strftime(start_date, f"%d/%m/%y %H:%M:%S")
    end_date_str = datetime.strftime(end_date, f"%d/%m/%y %H:%M:%S")

    apple_script = f'''
    set givenCalendar to "{calendar}"
    set startDate to date "{start_date_str}"
    set endDate to date "{end_date_str}"
    tell application "Calendar"
        set output to ""


        set calendarExists to false
        repeat with c in calendars
            if name of c is givenCalendar then
                set calendarExists to true
                exit repeat
            end if
        end repeat

        if calendarExists is false then
            return "[Error] Calendar '" & givenCalendar & "' not found."
        end if

        set target_calendar to calendar givenCalendar

        set calName to name of target_calendar
        try
            set theEvents to every event of target_calendar
            repeat with anEvent in theEvents
                if (start date of anEvent) ≥ startDate and (start date of anEvent) ≤ endDate then
                    set evSummary to summary of anEvent
                    set evStart to start date of anEvent as string
                    set evEnd to end date of anEvent as string
                    set output to output & "Event: " & evSummary & "|" & evStart & "|" & evEnd & ";"
                end if
            end repeat
        on error errMsg
            set output to output & "    [Error reading events: " & errMsg & "]\n"
        end try
        return output
    end tell
    '''

    # Check if Calendar is running
    check_calendar = subprocess.run(
        ["osascript", "-e", 'tell application "System Events" to (name of processes) contains "Calendar"'],
        stdout=subprocess.PIPE, text=True
    )

    if "false" in check_calendar.stdout:
        # Open Calendar in background mode
        subprocess.run(["osascript", "-e", 'tell application "Calendar" to activate'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    
    process = subprocess.run(
        ['osascript', '-e', apple_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Data processing:
    # Transform process output to list
    process.stdout = process.stdout.split(';')
    process.stdout = process.stdout[:len(process.stdout)-1]
    
    # Structure datetime data into datetime object to sort chronologically
    timetable = []
    for element in process.stdout:
        element = element.split('|')
        event = element[0].strip()

        try:
            # Turn calendar output to datetime object
            start_date = datetime.strptime(element[1],"%A, %d %B %Y at %H:%M:%S")
            end_date = datetime.strptime(element[2],"%A, %d %B %Y at %H:%M:%S")


        except ValueError as e:
            print(f"Error parsing dates for event '{event}': {e}")
            continue


        timetable.append((event,start_date,end_date))
    
    # Sort every event chronologically with element of index 1: start date
    timetable = sorted(timetable, key=lambda date: date[1])

    if process.returncode != 0: 
        return process.stderr
    else:
        return timetable
    
def add_calendar_event(start_date:datetime, end_date:datetime, event:str, calendar="osiris") -> None:

    start_date_str = datetime.strftime(start_date, f"%d/%m/%Y %H:%M:%S")
    end_date_str = datetime.strftime(end_date, f"%d/%m/%Y %H:%M:%S")

    apple_script = f'''
    set startDate to date "{start_date_str}"
    set endDate to date"{end_date_str}"
    set eventTitle to "{event}"
    set givenCalendar to "{calendar}"

    tell application "Calendar"
        tell calendar givenCalendar
            make new event with properties {{summary: eventTitle, start date: startDate, end date: endDate}}
        end tell
    end tell
    '''
    process = subprocess.run(['osascript','-e',apple_script],stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if process.returncode != 0:
        print(f"Error: {process.stderr.strip()}")
    else:
        print(f"\nevent: {event} | start date: {start_date} | end date: {end_date} --> successfully added!")
        pass

def clearCal(calendar="osiris") -> None:
    apple_script = f''' 
    set givenCalendar to "{calendar}"
    tell application "Calendar"
        tell calendar givenCalendar
            delete (every event)
        end tell
    end tell
    '''
    process = subprocess.run(['osascript','-e',apple_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text= True)
    if process.returncode != 0:
        print(f"Error: {process.stderr.strip()}")
    else:
        print("calendar clear successfully")

def getFreeSlots(end_date:datetime, occupied_slots: list[str,datetime,datetime], work_start_time=time(10,00,00), work_end_time=time(19,30,00)) -> list[tuple[datetime,datetime]]:

    # for element in occupied_slots:
    #     print(f"event: {element[0]} | start_time: {element[1]} | end_time: {element[2]}")

    current_date = datetime.today()
    # Set boundaries for work time
    available_slots = []

    while current_date <= end_date:
        
        if current_date.date() == datetime.today().date():
            work_start = current_date
        else:
            work_start = datetime.combine(current_date.date(), work_start_time)
        
        work_end = datetime.combine(current_date.date(), work_end_time)
        if work_end < work_start:
            current_date += timedelta(days=1)
            continue

        free_slots = [(work_start,work_end)]

        for event in occupied_slots:
            event_start = event[1]
            event_end = event[2]
            for slot in free_slots:
                # Case 1: event fits completely in slot, slot is than divided in 2, leaving event size gap
                if event_start >= slot[0] and event_end <= slot[1]:
                    index = free_slots.index(slot)
                    free_slots.pop(index)
                    free_slots.insert(index,(slot[0],event_start))
                    free_slots.insert(index+1,(event_end,slot[1]))

                # Case 2: event starts before slots and end during slot, change slot to start at end of event
                elif event_start <= slot[0] and event_end > slot[0] and event_end < slot[1]:
                    index = free_slots.index(slot)
                    free_slots.pop(index)
                    free_slots.insert(index, (event_end, slot[1]))
                
                # Case 3: event starts after slot start and end after end of slot, change slot to end at start of event
                elif event_start > slot[0] and event_start < slot[1] and event_end >= slot[1]:
                    index = free_slots.index(slot)
                    free_slots.pop(index)
                    free_slots.insert(index, (slot[0], event_start))

                # Case 4: event starts before and ends after slor, remove slot
                elif event_start <= slot[0] and event_end >= slot[1]:
                    free_slots.remove(slot)


        available_slots.extend(free_slots)
        current_date = current_date + timedelta(days=1)
    
    return available_slots

            




if __name__ == '__main__':
    # Specify your date range here.
    # Make sure the date format matches what AppleScript expects.
    # For example: "January 1, 2022 00:00:00" might work on many systems.
    start_date = datetime.today().date()
    end_date = datetime.today() + timedelta(days=7)
    clearCal()
    # inc_week = get_calendar_events(start_date_str,end_date_str)
    # for event in inc_week:
    #     print(event)
    
    
    # av=getFreeSlots(start_date, end_date,'UOE','osiris','Personal Calendar')
    # for element in av:
    #     print(element,'\n')
    #     add_calendar_event(start_date=element[0],end_date=element[1], event='test func add calendar event', calendar='osiris')
    
    