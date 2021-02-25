from kivy.app import App
from kivy.lang import Builder
kv = '''
BoxLayout:
    padding: dp(100)
    Button:
        canvas.before:
            Color:
                rgba:(1,0,0,0.5)
            RoundedRectangle:
                size: self.width +dp(20), self.height+dp(20)
                pos: self.x - dp(10), self.y - dp(10)
                radius: 5,5,5,5
        background_color: (1,1,0,0.5)
        background_normal: ''
        background_down: ''
'''
class MyApp(App):
    def build(self):
        return Builder.load_string(kv)
 
if __name__  == '__main__':
    MyApp().run()