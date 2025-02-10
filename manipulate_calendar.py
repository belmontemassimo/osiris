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

def availability(start_date_str, end_date_str):
    active_instants = get_calendar_events(start_date_str, end_date_str)

    if type(active_instants) != list:
        return None
    
    inactive_instants = [(start_date_str,end_date_str)]
    for element in active_instants:
        for r in inactive_instants:
            if element[1] >= r[0] and element[2] <= r[1]:
                index = inactive_instants.index(r)
                inactive_instants.pop(index)
                inactive_instants.insert(index,(r[0],element[1]))
                inactive_instants.insert(index+1,(element[2],r[1]))
    return inactive_instants

if __name__ == '__main__':
    print('start')
    # Specify your date range here.
    # Make sure the date format matches what AppleScript expects.
    # For example: "January 1, 2022 00:00:00" might work on many systems.
    start_date_str = datetime.date.strftime(datetime.date.today(),"%d/%m/%Y %H:%M:%S")
    end_date_str = datetime.date.strftime(datetime.date.today() + datetime.timedelta(days=7), "%d/%m/%Y %H:%M:%S")

    inc_week = get_calendar_events(start_date_str,end_date_str)
    for event in inc_week:
        print(event)
    # print(availability(start_date_str, end_date_str))
    # add_calendar_event(start_date='07/02/2025 00:00:00',end_date='07/02/2025 10:35:00', event='test func add calendar event', calendar='osiris')
    # clear_calendar()
    print('end')