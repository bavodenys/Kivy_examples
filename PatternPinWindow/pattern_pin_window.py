from kivymd.app import MDApp
from kivy.app import App
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.button import ButtonBehavior
from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.uix.label import MDLabel
from kivy.properties import NumericProperty, BooleanProperty
from kivy.graphics.vertex_instructions import Line, Ellipse
from kivy.graphics import Color


# Calibrations
WINDOW_WIDTH = dp(500)
WINDOW_HEIGHT = dp(800)
MAX_ATTEMPTS = 3
TOUCH_MARGIN = 25
DOT_RADIUS = 25
CONFIRM_RADIUS = 50

class PatternDot(ButtonBehavior, MDLabel):
    dot_radius = NumericProperty(DOT_RADIUS)


class PatternPinWindow(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        MDApp = App.get_running_app()
        self.pattern_x = MDApp.pattern_x
        self.pattern_y = MDApp.pattern_y
        self.pattern_pin = MDApp.pattern_pin
        self.pattern_box = []
        self.dot_pos_fetched = False
        self.dots = {}
        self.dots_touched = []
        self.dots_confirmed = []
        self.attempts = 0
        self.connected_lines = []
        self.touch_line_on_canvas = False
        for i in range(self.pattern_y):
            self.pattern_box.append(MDBoxLayout(orientation='horizontal', size_hint=(1,1)))
            for j in range(self.pattern_x):
                pattern_dot = PatternDot()
                self.pattern_box[i].add_widget(pattern_dot)
            self.ids['pattern_box'].add_widget(self.pattern_box[i])

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            self.dot_touched(touch.pos)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.dot_touched(touch.pos)

    def on_touch_up(self, touch):
        # Try removing the touch line
        if self.touch_line_on_canvas:
            self.canvas.remove(self.touch_line)
            self.touch_line_on_canvas = False
        else:
            pass
        self.validate_pattern()

    def dot_touched(self, touch_pos):
        # Fetch the dot positions, only first iteration
        if not(self.dot_pos_fetched):
            for i in range(self.pattern_y):
                for j in range(self.pattern_x):
                    dot_canvas_pos = self.children[0].children[i].children[j].pos
                    dot_canvas_size = self.children[0].children[i].children[j].size
                    self.dots[i*self.pattern_x+j]= {'pos':[dot_canvas_pos[0]+dot_canvas_size[0]/2,
                                                    dot_canvas_pos[1]+dot_canvas_size[1]/2],
                                                    'x': self.pattern_x-1-j, 'y': self.pattern_y-1-i}
            self.dot_pos_fetched = True
        else:
            pass

        for dot in self.dots:
            if (abs(self.dots[dot]['pos'][0]-touch_pos[0])<= TOUCH_MARGIN and
                    abs(self.dots[dot]['pos'][1]-touch_pos[1])<= TOUCH_MARGIN):
                if dot in self.dots_touched:
                    pass
                else:
                    self.dots_touched.append(dot)
                    with self.canvas:
                        color = Color(1,0,0)
                        x = self.dots[self.dots_touched[-1]]['pos'][0] - CONFIRM_RADIUS/2
                        y = self.dots[self.dots_touched[-1]]['pos'][1] - CONFIRM_RADIUS/2

                        confirm_dot = Ellipse(pos=[x, y],size=[CONFIRM_RADIUS, CONFIRM_RADIUS])
                        self.dots_confirmed.append(confirm_dot)


        # Connect dots
        if len(self.dots_touched) >= 2:
            with self.canvas:
                color = Color(1,0,0)
                # Get position of last and second to last dot touched
                x1 = self.dots[self.dots_touched[-2]]['pos'][0]
                y1 = self.dots[self.dots_touched[-2]]['pos'][1]
                x2 = self.dots[self.dots_touched[-1]]['pos'][0]
                y2 = self.dots[self.dots_touched[-1]]['pos'][1]
                self.connected_lines.append(Line(points=(x1, y1, x2, y2), width=5))

        # Connect last dot with touch position
        if len(self.dots_touched) >= 1:
            # Try removing the touch line
            if self.touch_line_on_canvas:
                self.canvas.remove(self.touch_line)
            else:
                pass
            with self.canvas:
                color = Color(1,0,0)
                x1 = self.dots[self.dots_touched[-1]]['pos'][0]
                y1 = self.dots[self.dots_touched[-1]]['pos'][1]
                x2 = touch_pos[0]
                y2 = touch_pos[1]
                self.touch_line = Line(points=(x1, y1, x2, y2), width=5)
                self.touch_line_on_canvas = True


    def validate_pattern(self):
        # Remove the connected lines
        for line in self.connected_lines:
            self.canvas.remove(line)

        # Remove the confirm dots
        for confirm_dot in self.dots_confirmed:
            self.canvas.remove(confirm_dot)

        pattern_pin_ok = True
        if len(self.dots_touched) == len(self.pattern_pin):
            for i in range(len(self.dots_touched)):
                if self.dots[self.dots_touched[i]]['x'] == self.pattern_pin[i][0] \
                        and self.dots[self.dots_touched[i]]['y'] == self.pattern_pin[i][1]:
                    pass
                else:
                    pattern_pin_ok = False
            if pattern_pin_ok:
                MDApp = App.get_running_app()
                MDApp.code_pattern_ok = True
                MDApp.stop()
        else:
            pass

        self.attempts += 1
        if self.attempts >= MAX_ATTEMPTS:
            MDApp = App.get_running_app()
            MDApp.code_pattern_ok = False
            MDApp.stop()
        else:
            # Reinitialize
            self.dots_touched = []
            self.connected_lines = []
            self.dots_confirmed = []


class MainApp(MDApp):
    code_pattern_ok = BooleanProperty(False)

    def __init__(self, pattern_x, pattern_y, pattern_pin, **kwargs):
        super().__init__(**kwargs)
        self.pattern_x = pattern_x
        self.pattern_y = pattern_y
        self.pattern_pin = pattern_pin

    def build(self):
        self.title = "Pattern PIN"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        Builder.load_file("layout.kv")
        return PatternPinWindow()


# Example how to use the PIN window
if __name__ == "__main__":
    try:
        pattern_pin = [[0,0], [1,1], [2,2], [3,3]]
        pattern_x = 4
        pattern_y = 4
        app = MainApp(pattern_x, pattern_y, pattern_pin)
        app.run()
        if app.code_pattern_ok:
            print('Code pattern is OK')
        else:
            print('Code pattern is NOK!')
    except:
        pass
