import subprocess
import datetime

def get_calendar_events(start_date_str:str, end_date_str:str, calendar="UOE"):
    # Get data from calendar app through apple script
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

        event_name = element[0].strip()

        try:
            start_date = datetime.datetime.strptime(element[1],"%A, %d %B %Y at %H:%M:%S")
            start_date = datetime.datetime.strftime(start_date, "%d/%m/%Y %H:%M:%S")

            end_date = datetime.datetime.strptime(element[2],"%A, %d %B %Y at %H:%M:%S")
            end_date = datetime.datetime.strftime(end_date, "%d/%m/%Y %H:%M:%S")

        except ValueError as e:
            print(f"Error parsing dates for event '{event_name}': {e}")
            continue



        timetable.append((element[0],start_date,end_date))
    
    # Sort every event chronologically with element of index 1: start date
    timetable = sorted(timetable, key=lambda date: datetime.datetime.strptime(date[1], "%d/%m/%Y %H:%M:%S"))

    if process.returncode != 0: 
        return process.stderr
    else:
        return timetable
    
def add_calendar_event(start_date:str, end_date:str, event:str, calendar="osiris"):

    apple_script = f'''
    set startDate to date "{start_date}"
    set endDate to date"{end_date}"
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
        print("event successfully added")
    
def clear_calendar(calendar="osiris"):
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

def availability(start_date_str:str, end_date_str:str, work_end_str='20:00:00', work_start_str='09:30:00'):

    if not start_date_str:
        start_date_str = datetime.date.strftime(datetime.date.today(),"%d/%m/%Y %H:%M:%S")
    if not end_date_str:
        end_date_str = datetime.date.strftime(datetime.date.today() + datetime.timedelta(days=7), "%d/%m/%Y %H:%M:%S")

    occupied_slots = get_calendar_events(start_date_str, end_date_str)

    
    if type(occupied_slots) != list:
        return None
    
    # Transform current date and end date to datetime object
    try:
        current_date = datetime.datetime.today().date()
        end_date = datetime.datetime.strptime(end_date_str, "%d/%m/%Y %H:%M:%S").date()

    except ValueError:
        return None
    
    # Set boundaries for work time
    work_start_time = datetime.datetime.strptime(work_start_str, "%H:%M:%S").time()
    work_end_time = datetime.datetime.strptime(work_end_str, "%H:%M:%S").time()

    available_slots = []

    while current_date < end_date:

        work_start = datetime.datetime.combine(current_date, work_start_time)
        work_end = datetime.datetime.combine(current_date, work_end_time)

        inactive_instants = [(work_start,work_end)]

        for event_str in occupied_slots:
            event_start = datetime.datetime.strptime(event_str[1], "%d/%m/%Y %H:%M:%S")
            event_end = datetime.datetime.strptime(event_str[2], "%d/%m/%Y %H:%M:%S")
            for slot in inactive_instants:
                # Case 1: event fits completely in slot, slot is than divided in 2, leaving event size gap
                if event_start >= slot[0] and event_end <= slot[1]:
                    index = inactive_instants.index(slot)
                    inactive_instants.pop(index)
                    inactive_instants.insert(index,(slot[0],event_start))
                    inactive_instants.insert(index+1,(event_end,slot[1]))

                # Case 2: event starts before slots and end during slot, change slot to start at end of event
                elif event_start <= slot[0] and event_end > slot[0] and event_end < slot[1]:
                    index = inactive_instants.index(slot)
                    inactive_instants.pop(index)
                    inactive_instants.insert(index, (event_end, slot[1]))
                
                # Case 3: event starts after slot start and end after end of slot, change slot to end at start of event
                elif event_start > slot[0] and event_start < slot[1] and event_end >= slot[1]:
                    index = inactive_instants.index(slot)
                    inactive_instants.pop(index)
                    inactive_instants.insert(index, (slot[0], event_start))

                # Case 4: event starts before and ends after slor, remove slot
                elif event_start <= slot[0] and event_end >= slot[1]:
                    inactive_instants.remove(slot)

        
        inactive_instants_str = []
        for slot in inactive_instants:
            temp_slot = list()
            for element in slot:
                temp_slot.append(datetime.datetime.strftime(element, "%d/%m/%Y %H:%M:%S"))
            inactive_instants_str.append(tuple(temp_slot))

        available_slots.extend(inactive_instants_str)

        current_date = current_date + datetime.timedelta(days=1)
    
    return available_slots

            




if __name__ == '__main__':
    # Specify your date range here.
    # Make sure the date format matches what AppleScript expects.
    # For example: "January 1, 2022 00:00:00" might work on many systems.
    start_date_str = datetime.date.strftime(datetime.date.today(),"%d/%m/%Y %H:%M:%S")
    end_date_str = datetime.date.strftime(datetime.date.today() + datetime.timedelta(days=7), "%d/%m/%Y %H:%M:%S")

    # inc_week = get_calendar_events(start_date_str,end_date_str)
    # for event in inc_week:
    #     print(event)
    av=availability(start_date_str, end_date_str)
    for element in av:
        print(element,'\n')
    # add_calendar_event(start_date='07/02/2025 00:00:00',end_date='07/02/2025 10:35:00', event='test func add calendar event', calendar='osiris')
    # clear_calendar()
