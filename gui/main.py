from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.

kv = Builder.load_file("my.kv")
sm = ScreenManager()

# Declare both screens
class LoginScreen(Screen):
    def btn(self):
        sm.current = 'second'

class SecondScreen(Screen):
    pass

class TestApp(App):
    def build(self):
        # Create the screen manager
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SecondScreen(name='second'))

        sm.current = 'login'

        return sm



if __name__ == '__main__':
    TestApp().run()