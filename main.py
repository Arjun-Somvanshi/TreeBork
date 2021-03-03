from kivy.app import App
from kivy.config import Config
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '750')
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition, SlideTransition
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.properties import StringProperty, ListProperty, DictProperty, BooleanProperty
from kivy.utils import rgba as RGBA
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.utils import platform
from functools import partial
from kivy.animation import Animation
import time
import json
import os

app = None

if platform != 'android':
    Window.minimum_width = dp(500)  
    Window.minimum_height = dp(600)

def quick_message(title, message):
    design = QuickMessage()
    design.ids.title.text = title
    design.ids.message.text = message
    error_dialogue = CustomModalView(
                                        size_hint = (0.35, 0.2),
                                        size_hint_max = (dp(400), dp(300)),
                                        size_hint_min = (dp(250), dp(200)),
                                        auto_dismiss = False,
                                        opacity = 0,
                                        overlay_color = (0,0,0,0.5)
    )
    error_dialogue.add_widget(design)
    error_dialogue.open({'center_x': 0.5, 'center_y': 2}, {'center_x': 0.5, 'center_y': 0.5}, 'out_expo')
    design.ids.close.bind(on_release = partial(error_dialogue.dismiss, {'center_x': 2, 'center_y': 0.5}, 'in_expo', 0.5, 0.75, True))

class CustomModalView(ModalView): # here I have made a custom modal view so that it can handle animations 
                                  # instead of typing the whole deal over and over, the open and dismiss are new                  
    def open(self, pos_hint_initial = {}, pos_hint_final = {}, 
             t = '', d1=0.7, d2=0.7, animate = True, *largs, **kwargs):
        global app
        #print(app.animations)
        if animate and app.animations: # we have to parameters to decide whether animation should occur or
        # not, incase, the user decides to not use animations on slow hardware, app.animations will be set to false, 
        # if the developer doen't wanna use the animation then he/she can set animate to false
            self.disabled = True
            self.pos_hint = pos_hint_initial
            anim = Animation(pos_hint = pos_hint_final, t = t, duration = d1)
            anim &= Animation(opacity = 1, t=t, duration=d2)
            anim.start(self)
            anim.bind(on_complete=self.enable_popup)
        else: 
            self.opacity = 1
            self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        super(CustomModalView, self).open(*largs, **kwargs)
    
    def enable_popup(self, *args):
        self.disabled = False
    
    def dismiss(self, pos_hint_final = {}, t = '', d1=0.7, d2=0.75, animate = True, *largs, **kwargs):
        #print('dismissing')
        self.disabled = True
        if animate and app.animations:
            anim = Animation(pos_hint = pos_hint_final, t = t, duration = d1)
            anim &= Animation(opacity = 0, t=t, duration = d2)
            anim.start(self)
            anim.bind(on_complete = self.finish_dismiss) # binding the on_complete callback, to finish dismiss()
        else:
            super(CustomModalView, self).dismiss()

    def finish_dismiss(self, *args):
        super(CustomModalView, self).dismiss()

class QuickMessage(BoxLayout):
    pass
    
class SlotButton(Button):
    slot_text = StringProperty('')
    def on_release(self):
        global app
        UserInput_screen = app.root.get_screen('UserInput')
        UserInput_screen.add_slot(self.slot_text)

class UserInput(Screen):
    theory_slots = DictProperty({})
    lab_slots = DictProperty({})
    schedule_type = StringProperty('')
    slot_data = ListProperty([])
    def __init__(self, **kwargs):
        super(UserInput, self).__init__(**kwargs)
        # defining all of the given slots for the timetable
 
        self.theory_slots = {
                                'monday': ['A1', 'F1', 'D1', 'TB1', 'TG1', 
                                           'A2', 'F2', 'D2', 'TB2', 'TG2', 'V3'],

                                'tuesday': ['B1', 'G1', 'E1', 'TC1', 'TAA1', 
                                            'B2', 'G2', 'E2', 'TC2', 'TAA2', 'V4'],

                                'wednesday': ['C1', 'A1', 'F1', 'V1', 'V2',
                                              'C2', 'A2', 'F2', 'TD2', 'TBB2', 'V5'],
                                
                                'thursday':['D1', 'B1', 'G1', 'TE1', 'TCC1',
                                            'D2', 'B2', 'G2', 'TE2', 'TCC2', 'V6'],
                                            
                                'friday':['E1', 'C1', 'TA1', 'TF1', 'TD1',
                                          'E2', 'C2', 'TA2', 'TF2', 'TDD2', 'V7'],

                                'saturday':['V8', 'X11', 'X12', 'Y11', 'Y12',
                                            'X21', 'Z21', 'Z22', 'W21', 'W22', 'V9',],
                                
                                'sunday': ['V10', 'Y11', 'Y12', 'X11', 'X12',
                                          'V10', 'W21', 'W22', 'Z21', 'Z22', 'V11']
                            }
        
        self.lab_slots = {
                                'monday': ['L'+str(x) for x in range(1,7)]+['L'+str(y) for y in range(31,37)], 

                                'tuesday': ['L'+str(x) for x in range(7,13)]+['L'+str(y) for y in range(42,43)],

                                'wednesday': ['L'+str(x) for x in range(13,19)]+['L'+str(y) for y in range(43,49)],
                                
                                'thursday':['L'+str(x) for x in range(19,25)]+['L'+str(y) for y in range(49,55)],
                                            
                                'friday':['L'+str(x) for x in range(25,31)]+['L'+str(y) for y in range(55,61)],

                                'saturday':['L'+str(x) for x in range(71,77)]+['L'+str(y) for y in range(83,89)],
                                
                                'sunday': ['L'+str(x) for x in range(77,83)]+['L'+str(y) for y in range(89,95)]
                            }

        self._theory_timings = [
                        [("8", "00"), ("8", "50")], 
                        [("9", "00"), ("9", "50")], 
                        [("10", "00"), ("10", "50")],
                        [("11", "00"), ("11", "50")], 
                        [("12", "00"), ("12", "50")], 
                        [("2", "00"), ("2", "50")],
                        [("3", "00"), ("3", "50")],
                        [("4", "00"), ("4", "50")],
                        [("5", "00"), ("5", "50")],
                        [("6", "00"), ("6", "50")],
                        [("7", "00"), ("7", "50")]
                       ]
        self._labs_timings = [
                        [("8", "00"), ("8", "45")], 
                        [("8", "46"), ("9", "30")], 
                        [("10", "00"), ("10", "45")],
                        [("10", "46"), ("11", "30")], 
                        [("11", "31"), ("12", "15")], 
                        [("12", "16"), ("1", "00")],
                        [("2", "00"), ("2", "45")],
                        [("2", "46"), ("3", "30")],
                        [("4", "00"), ("4", "45")],
                        [("4", "46"), ("5", "30")],
                        [("5", "31"), ("6", "15")],
                        [("6", "16"), ("7", "00")]
		      ]
    
    def screen_order(self):
        print('hello screen order has begun')
        if os.path.isfile("schedule_type.txt"):
            print('hello the screen is changing now')
            self.manager.transition = NoTransition()
            self.manager.current = 'main'
            self.ids.user_input_sc_manager.current = 'AddSubject'
    
    def set_schedule_type(self):
        print('setting the schedule')
        global app
        if self.ids.vit.enabled:
            self.schedule_type = 'VIT'
        else:
            self.schedule_type = 'Other'
        with open('schedule_type.txt', 'w') as f:
            f.write(self.schedule_type)
        self.ids.user_input_sc_manager.transition = SlideTransition(direction = 'left')
        self.ids.user_input_sc_manager.current = 'AddSubject'
        # this is a flag to define if this is the first time the app is being used or not 
        # if it's being used for the first time, the tutorial should initiate
        self.manager.get_screen('main').first_run = True
        
    def tutorial(self, tutorial_num, *args):
        # Now we bring in the tutorial popups for the explanation of the main screen
        tut1 = CustomModalView(
                                size_hint = (0.35, 0.2),
                                size_hint_max = (dp(400), dp(300)),
                                size_hint_min = (dp(250), dp(200)),
                                auto_dismiss = False,
                                opacity = 0,
                              )
        content = QuickMessage()
        if tutorial_num == 1:
            content.ids.title.text = 'Tutorial Message 1'
            content.ids.message.text = "To add subjects to the Time-Table click 'Add a subject'."
            pos_initial = {'x': 0.05, 'y': 2}
            pos_final =   {'x': 0.05, 'y': 0.15}
            content.ids.close.bind(on_release = partial(tut1.dismiss, {'x': 2, 'y': 0.15}, 'in_quart', 0.5, 0.75, True ))
        
        elif tutorial_num == 2:
            content.ids.title.text = 'Tutorial Message 2'
            content.ids.message.text = "To check up the weekly schedule click on 'Weekly'."
            pos_initial = {'center_x': 0.5, 'y': 2}
            pos_final =   {'center_x': 0.5, 'y': 0.15}
            content.ids.close.bind(on_release = partial(tut1.dismiss, {'center_x': 2, 'y':0.15}, 'in_quart', 0.5, 0.75, True ))
        
        elif tutorial_num == 3:
            content.ids.title.text = 'Tutorial Message 3'
            content.ids.message.text = "To change app settings click on Settings."
            pos_initial = {'right': 0.95, 'y': 2}
            pos_final =   {'right': 0.95, 'y': 0.15}
            content.ids.close.bind(on_release = partial(tut1.dismiss, {'right': 4, 'y':0.15}, 'in_quart', 0.5, 0.75, True ))

        elif tutorial_num == 4:
            content.ids.title.text = 'Tutorial Message 4'
            content.ids.message.text = "This is where todays time table would be."
            pos_initial = {'center_x': 0.5, 'center_y': 2}
            pos_final =   {'center_x': 0.5, 'center_y': 0.5}
            content.ids.close.bind(on_release = partial(tut1.dismiss, {'center_x': 2, 'y':0.15}, 'in_quart', 0.5, 0.75, True ))

        tut1.add_widget(content)
        main_screen = app.root.get_screen('main')

        tut1.open(pos_initial, pos_final, 'out_bounce', 0.7)
        
        tut1.bind(on_dismiss = partial(self.schedule_tutorial, tutorial_num + 1))    
    
    def schedule_tutorial(self, tut_num, *args):
        print('Hello I was called')
        if tut_num<=4:
            Clock.schedule_once(partial(self.tutorial, tut_num), 0.2)

    def next(self):
        '''To make available slots visible to the user while adding a new subject'''
        if self.ids.subject_name.text != '':
            #clearing slot_data before making anychanges at all
            self.slot_data = []
            # checking if this is the first subject to be added
            if os.path.isfile("slots.json"):
                self.first_added_subject = False

            else:
                self.first_added_subject = True
            # now we check if this is the first time a subject is being added, and then create the json file and start adding stuff to it
            if self.first_added_subject:
                # picking out the unique slots to display here
                temp_theory_slot_list = [] # this is a preliminary list which is used before adding data to the recycle view
                temp_lab_slot_list = []
                for key in self.theory_slots:
                    for slot in self.theory_slots[key]:
                        if slot not in temp_theory_slot_list:
                            temp_theory_slot_list.append(slot)
                # for the lab slots too, cause we gotta add them to the json file
                for key in self.lab_slots:
                    for slot in self.lab_slots[key]:
                        temp_lab_slot_list.append(slot)
                
                temp_theory_slot_list.sort() # sorting the list
                # now sorting the labslots
                sorted_list = []
                for ele in temp_lab_slot_list:
                    sorted_list.append(int(ele[1:]))
                sorted_list.sort()
                for i in range(len(temp_lab_slot_list)):
                    temp_lab_slot_list[i] = 'L' + str(sorted_list[i])

                if self.ids.theory.enabled:
                    temp_slot_list = temp_theory_slot_list# available_slots is a dictionary so beware
                else:
                    temp_slot_list = temp_lab_slot_list

                for slot in temp_slot_list:
                    self.slot_data.append({'slot_text': slot})

                # writing the available slots into json file
                with open('slots.json', 'w') as f:
                    json.dump({'theory_slots': temp_theory_slot_list, 'lab_slots': temp_lab_slot_list}, f)
            else:
                self.slot_data = []
                with open('slots.json') as f:
                    available_slots = json.load(f)
                    if self.ids.theory.enabled:
                        loaded_slots = available_slots['theory_slots']
                    else:
                        loaded_slots = available_slots['lab_slots']
                    for slot in loaded_slots:
                        self.slot_data.append({'slot_text': slot})

                
            # changing the screen to choose the slot
            self.ids.user_input_sc_manager.transition = SlideTransition(direction = 'left')
            self.ids.user_input_sc_manager.current = 'SlotScreen'
        else:
            quick_message('Subject Name', 'You need to give a subject name.')
    
    def add_slot(self, slot_name):
        if len(self.ids.chosen_slot.text.split('+'))<=6:
            for button in self.slot_data:
                if button['slot_text'] == slot_name:
                    index_to_pop = self.slot_data.index(button)
                    self.slot_data.pop(index_to_pop)
            # checkig if this is the first slot to be added
            if self.ids.chosen_slot.text[:7] == 'Example':
                self.ids.chosen_slot.text = slot_name 
            #if not the first slot then it's appended
            else:
                self.ids.chosen_slot.text += '+' + slot_name
        else:
            quick_message('Slot Error', 'You have added too many slots.')
    
    def clear(self):
        if self.ids.chosen_slot.text != 'Example: A1+TA1 or L3+L4':
            available_list = []
            slot_list = self.ids.chosen_slot.text.split('+')
            re_added_slot = slot_list[-1]
            slot_list.pop(-1)
            self.ids.chosen_slot.text = ''
            for slot in slot_list:
                if slot_list[-1] != slot:
                    self.ids.chosen_slot.text+= slot + '+'
                else:
                    self.ids.chosen_slot.text += slot 
            if self.ids.chosen_slot.text == '':
                self.ids.chosen_slot.text = 'Example: A1+TA1 or L3+L4'
            for slotbtn in self.slot_data:
                available_list.append(slotbtn['slot_text'])
            available_list.append(re_added_slot)
            # sorting the list after adding the element back to where it belongs
            if self.ids.theory.enabled:
                available_list.sort()
            else:
                temp_list = []
                for ele in available_list:
                    temp_list.append(int(ele[1:]))
                temp_list.sort()
                available_list = []
                for ele in temp_list:
                    available_list.append('L' + str(ele))
            self.slot_data = []
            for slot in available_list:
                self.slot_data.append({'slot_text':slot})
    
    def clear_all(self):
        for i in self.ids.chosen_slot.text.split('+'):
            self.clear()
    
    def refresh(self):
        self.ids.subject_name.text = ''
        self.ids.sub_code.text = ''
        self.ids.venue.text = ''
    
    def success_animation(self, subject_name):
        self.ids.success.opacity = 0
        self.ids.success.text = subject_name + ' was added to TreeBork.'
        anim = Animation(opacity =1, duration=2.5)
        anim.bind(on_complete = self.remove_success)
        anim.start(self.ids.success)

    def remove_success(self, *args):
        anim = Animation(opacity = 0, duration=2.5)
        anim.start(self.ids.success)
        

    def bubble_sort(self, day):
        for i in range(len(day)):
            for j in range(len(day)-i-1):
                if day[j]['rank']>day[j+1]['rank']:
                    temp = day[j]
                    day[j] = day[j+1]
                    day[j+1] = temp
        return day

    def add_subject(self):
        # adding the subject to the time table in this function

        if self.ids.chosen_slot.text != 'Example: A1+TA1 or L3+L4':
            # save the details
            subject_name = self.ids.subject_name.text
            subject_code = self.ids.sub_code.text
            venue = self.ids.venue.text
            slot_list = self.ids.chosen_slot.text.split('+')
            # set the chosen slot back to the hint text
            self.ids.chosen_slot.text = 'Example: A1+TA1 or L3+L4'
            # refresh the add subject screen
            self.refresh()
            json_data = []
            for slotbtn in self.slot_data:
                json_data.append(slotbtn['slot_text'])
            # changing the available slots after a subject has been added
            with open('slots.json', 'r') as f:
                previous_data = json.load(f)
            if self.ids.theory.enabled:
                with open('slots.json', 'w') as f:
                    json.dump({'theory_slots': json_data, 'lab_slots': previous_data['lab_slots']}, f)
            else:
                with open('slots.json', 'w') as f:
                    json.dump({'theory_slots': previous_data['theory_slots'], 'lab_slots': json_data}, f)
            
            # adding it to the time table:
            mainscreen = self.manager.get_screen('main')
                # checking if the time table exists
            if os.path.isfile('timetable.json'):
                self.time_table_exists = True
            else:
                self.time_table_exists = False
            # adding the stuff to the timetable dictionary 
            if self.ids.theory.enabled:
                time_table_dictionary = self.theory_slots
                time_of_slots = self._theory_timings
            else:
                time_table_dictionary = self.lab_slots
                time_of_slots = self._labs_timings
            
            for chosen_slot in slot_list:
                for day in time_table_dictionary:
                    for slot in time_table_dictionary[day]:
                        #print('Chosen: ',chosen_slot)
                        #print('Slot: ',slot)
                        if chosen_slot == slot:
                            print('matching slots')
                            index_of_slot = time_table_dictionary[day].index(slot)
                            # fetching time
                            print('this is the index: ', index_of_slot)
                            timing = time_of_slots[index_of_slot]
                            time_as_string = str(timing[0][0]) + ':' + str(timing[0][1])
                            time_as_string += ' - ' + str(timing[1][0]) + ':' + str(timing[1][1])

                            slot_details = {
                                                'subject_name': subject_name,
                                                'subject_code': subject_code,
                                                'slot': slot,
                                                'time': time_as_string,
                                                'venue': venue,
                                                'rank': index_of_slot,
                                            }
                            mainscreen.timetable[day].append(slot_details)
            for day in mainscreen.timetable:
                mainscreen.timetable[day] = self.bubble_sort(mainscreen.timetable[day])
            mainscreen.set_data()
            print('This is the data: ', mainscreen.data)

            with open('timetable.json', 'w') as f:
                json.dump(mainscreen.timetable, f, indent = 2)
            # switching screens back to the addsubject
            self.ids.user_input_sc_manager.transition = SlideTransition(direction = 'right')
            self.ids.user_input_sc_manager.current = 'AddSubject'
            self.success_animation(subject_name)
        else:
            quick_message('Empty Slot', 'No slot was chosen.')
        
class Tile(GridLayout):
    subject_name = StringProperty('')
    subject_code = StringProperty('')
    academic_block = StringProperty('')
    time = StringProperty('')
    slot = StringProperty('')

class MainScreen(Screen):
    
    timetable = DictProperty({'monday':[], 'tuesday':[],'wednesday':[],'thursday':[],'friday':[],'saturday':[], 'sunday':[]})
    data = ListProperty([])
    first_run = False
    
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        if os.path.isfile('timetable.json'):
            with open('timetable.json', 'r') as f:
                self.timetable = json.load(f)
            Clock.schedule_once(self.set_data)
        

    def set_data(self, *args):
        # to set the data to the appropriate day
        print('SET DATA was called')
        global app
        today = app.time.split(' ')[0].lower()
        self.data = []
        for day in self.timetable:
            if day[:3] == today:
                print('setting the data')
                for slot_details in self.timetable[day]:
                    print('The data list is appending')
                    self.data.append({
                                        'subject_name': slot_details['subject_name'],
                                        'subject_code': slot_details['subject_code'],
                                        'slot': slot_details['slot'],
                                        'time': slot_details['time'],
                                        'academic_block': slot_details['venue'],
                                    })
                break
        a = 0
        for btn in self.ids.weekbar.walk(restrict=True):
            if a != 0:
                if btn.text.lower() == today:
                    btn.week = True
            a+=1

    def on_enter(self):
        print('Is this the first run?: ', self.first_run)
        if self.first_run:
            print('Is this the first run?: ', self.first_run)
            self.manager.get_screen('UserInput').tutorial(1)
            self.first_run = False
            #pass
    def add_subject(self):
        self.manager.transition = SlideTransition(direction= 'right')
        self.manager.current = 'UserInput'
        # the lines below ensure that the screen on the UserInput is AddSubject
        UserInput_screen = self.manager.get_screen('UserInput') # getting the UserInput screen
        UserInput_screen.ids.user_input_sc_manager.transition = NoTransition()
        UserInput_screen.ids.user_input_sc_manager.current = 'AddSubject'
    
    def show_day(self, text):
        self.data = []
        for day in self.timetable:
            if day[:3] == text.lower():
                print('New day was found')
                for slot_details in self.timetable[day]:
                    print('The data list is appending for the new day')
                    self.data.append({
                                        'subject_name': slot_details['subject_name'],
                                        'subject_code': slot_details['subject_code'],
                                        'slot': slot_details['slot'],
                                        'time': slot_details['time'],
                                        'academic_block': slot_details['venue'],
                                    })
                break
        a = 0
        for btn in self.ids.weekbar.walk(restrict=True):
            if a != 0:
               #print('Object from the weekbar: ', type(btn))
               #print('btn text and the text parameter: ', btn.text.lower(), text)
                if btn.text.lower() == text.lower():
                    print('the btn week was changed to true from show day')
                    btn.week = True
                else:
                    btn.week = False
            a+=1


class TimeTableScreen(Screen):
    pass

class Screen_Manager(ScreenManager):
    pass

class TimeTableApp(App):
    treebork = {'tile_grid': '#1E2E0A', 
                'tile_background': '#0B2708', 
                'tile_label': '#385C00', 
                'cols':'#2A3E04', 
                'main_fonts': '#f1c40f',
                'secondary_color': '#a2d9ce', 
                'button': '#576e12', 
                'buttondown': '#34420a'}
    
    moonsugar = {'tile_grid': '#6A5ACD', 
                'tile_background': '#483D8B', 
                'tile_label': '#4169E1', 
                'cols':'#4B0082', 	 
                'main_fonts': '#64b5f6', 
                'secondary_color': '#a2d9ce', 
                'button': '#2e86c1', 
                'buttondown': '#5dade2'}
    
    acid      = {'tile_grid': '#1E2E0A', 
                'tile_background': '#0B2708', 
                'tile_label': '#385C00', 
                'cols':'#2A3E04', 
                'main_fonts': '#f1c40f', 
                'secondary_color': '#a2d9ce', 
                'button': '#576e12', 
                'buttondown': '#34420a'}
    
    purplehaze = {'tile_grid': '#1E2E0A', 
                'tile_background': '#0B2708', 
                'tile_label': '#385C00', 
                'cols':'#2A3E04', 
                'main_fonts': '#f1c40f', 
                'secondary_color': '#a2d9ce', 
                'button': '#576e12', 
                'buttondown': '#34420a'}

    theme = moonsugar
    plat = None
    animations = True
    time = StringProperty('')
    def on_start(self):
        self.root.get_screen('UserInput').screen_order()
    def build(self):
        
        global app
        Window.clearcolor = RGBA(self.theme['cols'])
        self.plat = platform
        app = self
        self.assign_time()
    def set_btn_col(self, ch, btn):
        if ch==0:
            btn.background_color = self.theme['buttondown']
        elif ch == 1:
            btn.background_color = self.theme['button']
        elif ch == 2:
            btn.background_color = self.theme['tile_grid']
    def assign_time(self, *args):
        self.time = time.asctime(time.localtime(time.time()))
    

if __name__ == '__main__':
    TimeTableApp().run()
