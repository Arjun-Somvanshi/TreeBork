from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, OptionProperty, ListProperty, BooleanProperty
from kivy.metrics import sp, dp
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from functools import partial
from kivy.animation import Animation
Builder.load_string( '''
<UIDropDownItem>:
    canvas.before:
        Color:
            rgba: ((root.item_color[0] if self.state == 'normal' else root.item_color[1]) if root.rounded == False else (0,0,0,0))
        Rectangle:
            size: self.size
            pos: self.pos
        Color: 
            rgba: ((root.item_color[0] if self.state == 'normal' else root.item_color[1]) if root.rounded == True else (0,0,0,0))
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [self.height/2]
    background_color: (1,1,1,0)
    background_normal: root.background_img_normal
    backgrond_down: root.background_img_down
    font_name: root.item_font
    font_size: root.item_font_size
    color: root.item_font_color
    shorten: True
    shorten_from: 'right'
    text_size: self.width - dp(5), None
    halign: 'center'

<UIDropDownContent>:
    canvas.before:
        Color:
            rgba: root.background_color 
        Rectangle:
            size: self.size
            pos: self.pos
    RecycleView:
        id: dropdownrv
        viewclass: 'UIDropDownItem'        
        data: root.Elements
        RecycleBoxLayout:
            default_size_hint: root.item_size_hint_x, None
            default_size: None, root.item_height 
            spacing: dp(15)
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
            padding: dp(20)
<UIDropDown>: 
    default_item: ''
    elements: []
    dd_size: [self.dd_width, self.dd_height]
    dd_width: dp(400)
    dd_height: dp(400)
    dd_background_color: [0,0,0,1]
    dd_item_height: dp(30)
    dd_item_color: [[1,1,1,1], [1,1,1,0.5]]
    dd_item_isrounded: False
    dd_item_img_down: self.background_down
    dd_item_img_normal: self.background_normal
    dd_item_size_hint_x: 1
    dd_item_font_size: sp(15)
    dd_item_font_color: [0,0,0,1]
    dd_item_font: 'Roboto'
    show_items: 1 
    calculate_ddheight: False
    text: self.default_item
''')

class UIDropDownItem(Button):
    owner = ObjectProperty()
    dd_object = ObjectProperty()
    rounded = BooleanProperty(False)
    item_color = ListProperty([[1,1,1,1], [1,1,1,0.5]])
    item_font = StringProperty('Roboto')
    item_font_size = NumericProperty(sp(15))
    item_font_color = ListProperty([0,0,0,1])
    background_img_normal = StringProperty('')
    background_img_down = StringProperty('')
    def on_release(self):
        self.owner.selected_item = self.text
        self.dd_object.dropdown_view.dismiss()

class UIDropDownContent(BoxLayout):
    Elements = ListProperty([]) 
    selected_item = StringProperty('')
    background_color = ListProperty([0,0,0,1])
    item_height = NumericProperty(dp(30))
    item_size_hint_x = NumericProperty(1)
    def __init__(self, dropdown_instance, elements: list, background_color: list, item_height = dp(30), **kwargs):
        super(UIDropDownContent, self).__init__(**kwargs)
        for element in elements:
            self.Elements.append({'text': element, 
                                  'owner': self, 
                                  'dd_object': dropdown_instance, 
                                  'item_color': dropdown_instance.dd_item_color,
                                  'background_img_down': dropdown_instance.dd_item_img_down,
                                  'background_img_normal': dropdown_instance.dd_item_img_normal,
                                  'rounded': dropdown_instance.dd_item_isrounded,
                                  'pos_hint': {'center_x': 0.5}, # this is how you would center widgets inside a recycle view
                                  'item_font': dropdown_instance.dd_item_font,
                                  'item_font_color': dropdown_instance.dd_item_font_color,
                                  'item_font_size': dropdown_instance.dd_item_font_size
                                  })
            self.background_color = background_color
            self.item_height = item_height
            self.item_size_hint_x = dropdown_instance.dd_item_size_hint_x
        

class UIDropDown(Button):
    dd_open_vertical = OptionProperty('down', options = ['up', 'down'])
    dd_open_horizontal = OptionProperty('center', options = ['left', 'center', 'right'])
    def calculate_minimum_height(self):
        required_height = 0
        for i in range(self.show_items):
            required_height += self.dd_item_height + dp(15)
        return required_height + dp(15)
    
    def __init__(self, **kwargs):
        self.register_event_type('on_set')
        super(UIDropDown, self).__init__(**kwargs)
    
    def on_set(self):
        pass

    def set_dropdown(self):
        self.content = UIDropDownContent(self, self.elements, self.dd_background_color, self.dd_item_height)
        if self.calculate_ddheight:
            self.dd_size[1] = self.calculate_minimum_height()
        self.dropdown_view = DropDownModalView(
                                           size_hint = (None, None),
                                           size = self.dd_size,
                                           overlay_color = (0,0,0,0)
                                       )
        if self.dd_open_vertical == 'down':
            vertical =  ['top',self.y/Window.height]
        elif self.dd_open_vertical == 'up':
            vertical = ['y', self.top/Window.height]
        if self.dd_open_horizontal == 'center':
            horizontal = ['center_x', self.center_x/Window.width]
        elif self.dd_open_horizontal == 'left':
            horizontal  = ['x', self.x/Window.width]
        elif self.dd_open_horizontal == 'right':
            horizontal = ['right', self.right/Window.width]
        self.dropdown_view.pos_hint = {horizontal[0]: horizontal[1], vertical[0]: vertical[1]}
        self.dropdown_view.add_widget(self.content)
        self.dropdown_view.bind(on_dismiss = self.set_selected_item)
        Window.bind(on_resize=partial(self.dropdown_view.dismiss, True))
    
    def on_release(self):
        self.set_dropdown()
        self.dropdown_view.open(self.dd_size[1])

    def set_selected_item(self, instance):
        if self.content.selected_item:
            self.text = self.content.selected_item
        self.dispatch('on_set')

class DropDownModalView(ModalView):
    def open(self, final_height, *largs, **kwargs):
        self.height = 0
        self.opacity = 0
        anim = Animation(height = final_height, t = 'in_expo', duration = 0.4)
        anim &= Animation(opacity=1, t='in_expo', duration = 0.4)
        anim.start(self)
        super(DropDownModalView, self).open(*largs, **kwargs)
    
    def dismiss(self, fast = False, *largs, **kwargs):
        if not fast:
            anim = Animation(height = 0, t='out_expo', duration=0.4)
            anim &= Animation(opacity = 0, t='out_expo', duration=0.4)
            anim.start(self)
            anim.bind(on_complete = self.finish_dismiss)
        else:
            super(DropDownModalView, self).dismiss()
    
    def finish_dismiss(self, *args):
        super(DropDownModalView, self).dismiss()
