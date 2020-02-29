import json
import urllib.request
import urllib.error

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder


Builder.load_string('''


<Container>:

    start_game_btn: start_game_btn
    add_question_btn: add_question_btn
    
    BoxLayout:
        padding: 5
        orientation: "vertical"

        Button:
            id: start_game_btn
            text: 'Начать игру'

            on_press:
                root.start_game()


        Button:
            id: add_question_btn
            text: 'Добавить вопрос'




<GameScreen>:
    questions: questions
    BoxLayout:
        orientation: 'vertical'
        RecycleView:
            id: questions
            viewclass: 'Button'
            RecycleBoxLayout:
                default_size: None, dp(56)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
''')


DOMAIN = 'http://127.0.0.1:8080'
API = {
    'start_game': urllib.request.urljoin(DOMAIN, 'game_mobile'),
}


class Container(Screen):
    def __init__(self, **kw):
            super(Container, self).__init__(**kw)

    def start_game(self):
        change_screen('game')

    def add_question(self):
        pass


class GameScreen(Screen):

    def on_enter(self, **kw):
        try:
            request = urllib.request.urlopen(API['start_game'])
        except urllib.error.HTTPError:
            pass
        else:
            qs = json.loads(request.read().decode("utf-8"))
            for q in qs:
                q_btn = Button(
                    text=q['text'],
                    on_press=lambda x: change_screen('main_menu'),
                    size_hint_y=None
                )
                self.questions.data.append({'text': q['text'], 'valign': 'top'})


sm = ScreenManager()
sm.add_widget(Container(name='main_menu'))
sm.add_widget(GameScreen(name='game'))
sm.current = 'main_menu'

def change_screen(screen):
    sm.current = screen


class GameApp(App):

    def build(self):
        return sm

GameApp().run()
