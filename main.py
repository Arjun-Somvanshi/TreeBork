from kivy.app import App
from kivy.config import Config
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition, SlideTransition
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.properties import StringProperty, ListProperty, DictProperty
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

class Tile(GridLayout):
    subject_name = StringProperty('')
    subject_code = StringProperty('')
    academic_block = StringProperty('')
    time = StringProperty('')
    slot = StringProperty('')
    
class SlotButton(Button):
    slot_text = StringProperty('')

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
                        [("8", "00"), ("9", "00")], 
                        [("9", "00"), ("9", "30")], 
                        [("10", "00"), ("11", "00")],
                        [("11", "00"), ("11", "30")], 
                        [("12", "00"), ("1", "00")], 
                        [("1", "00"), ("1", "30")],
                        [("3", "00"), ("4", "00")],
                        [("4", "00"), ("4", "30")],
                        [("5", "00"), ("6", "00")],
                        [("6", "00"), ("6", "30")],
                       ]
    
    def screen_order(self):
        print('hello screen order has begun')
        if os.path.isfile("schedule_type.txt"):
            print('hello the screen is changing now')
            self.manager.transition = NoTransition()
            self.manager.current = 'main'
            self.ids.user_input_sc_manager.current = 'AddSubject'
    
    def set_schedule_type(self):
        global app
        if self.ids.vit.enabled:
            self.schedule_type = 'VIT'
        else:
            self.schedule_type = 'Other'
        with open('schedule_type.txt', 'w') as f:
            f.write(self.schedule_type)
        self.ids.user_input_sc_manager.transition = SlideTransition(direction = 'left')
        self.ids.user_input_sc_manager.current = 'AddSubject'
        #initiating the tutorial
        #Clock.schedule_once(partial(self.tutorial, 1), 0.5)
        
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
            print(self.lab_slots)
            for key in self.lab_slots:
                print('This is a key: ', key)
                for slot in self.lab_slots[key]:
                    print('This is a slot: ', slot)
                    temp_lab_slot_list.append(slot)

            temp_theory_slot_list.sort() # sorting the list

            if self.ids.theory.enabled:
                temp_slot_list = temp_theory_slot_list# available_slots is a dictionary so beware
            else:
                temp_slot_list = temp_lab_slot_list

            for slot in temp_slot_list:
                self.slot_data.append({'slot_text': slot})

            # writing the available slots into json file
            #with open('slots.json', 'w') as f:
                #json.dump({'theory_slots': temp_theory_slot_list, 'lab_slots': temp_theory_slot_list}, f)
        else:
            with open('slots.json') as f:
                available_slots = json.load(f)
                self.slot_data = available_slots

            
        # changing the screen to choose the slot
        self.ids.user_input_sc_manager.transition = SlideTransition(direction = 'left')
        self.ids.user_input_sc_manager.current = 'SlotScreen'

    def add_subject(self):
        pass
        


class MainScreen(Screen):
    data = []
    def add_subject(self):
        self.manager.transition = SlideTransition(direction= 'right')
        self.manager.current = 'UserInput'
        # the lines below ensure that the screen on the UserInput is AddSubject
        UserInput_screen = self.manager.get_screen('UserInput') # getting the UserInput screen
        UserInput_screen.ids.user_input_sc_manager.transition = NoTransition()
        UserInput_screen.ids.user_input_sc_manager.current = 'AddSubject'


class TimeTableScreen(Screen):
    pass

class Screen_Manager(ScreenManager):
    pass

class TimeTableApp(App):
    tuborg = {'tile_grid': '#1E2E0A', 'tile_background': '#0B2708', 'tile_label': '#385C00', 
              'cols':'#2A3E04', 'main_fonts': '#f1c40f', 'secondary_color': '#a2d9ce', 
              'button': '#576e12', 'buttondown': '#34420a'}
    theme = tuborg
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
        Clock.schedule_interval(self.assign_time, 1)

    def assign_time(self, dt):
        self.time = time.asctime(time.localtime(time.time()))
    

if __name__ == '__main__':
    TimeTableApp().run()