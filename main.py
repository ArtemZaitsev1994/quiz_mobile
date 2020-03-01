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


<Question>:
    category_label: category_label
    complexity_label: complexity_label
    text_label: text_label
    answer_label: answer_label
    BoxLayout:
        orientation: 'vertical'
        Label:
            id: category_label
        Label:
            id: complexity_label
        Label:
            id: text_label
        Label:
            id: answer_label
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
        except (urllib.error.HTTPError, urllib.error.URLError):
            pass
        else:
            qs = json.loads(request.read().decode("utf-8"))
            self.questions.data = []
            for q in qs:
                q_btn = {
                    'text': q['text'],
                    'valign': 'top',
                    'on_press': lambda: change_screen(q['_id']),
                    'q_id': q['_id']
                }
                sm.add_widget(Question(q))
                self.questions.data.append(q_btn)


class Question(Screen):
    def __init__(self, question):
        super(Question, self).__init__()
        self.q = question
        self.name = question['_id']

    def on_enter(self):
        self.text_label.text = f'Вопрос: {self.q["text"]}'
        self.complexity_label.text = f'Сложность: {self.q["complexity"] * "*"}'
        self.category_label.text = f'Категория: {self.q["category"]}'
        self.answer_label.text = f'Ответ: {self.q["answer"]}'



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
