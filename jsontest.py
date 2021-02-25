import json
timetable = {'mon': 1, 'tue': 1, 'wed': 1, 'thurs': 1,}
available_slots = {'mon': 2, 'tue': 3, 'wed': 2, 'thurs': 3,}
with open('jsontest.json', 'a') as f:
    json.dump({'timetable':timetable}, f, indent = 2)
with open('jsontest.json', 'a') as f:
    json.dump({'available_slots':available_slots}, f, indent=2)
