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
    warning_label: warning_label
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
        Label:
            id: warning_label
            text: ""
        Button:
            id: back
            text: "Назад"
            on_press:
                root._going_back()


<Question>:
    category_label: category_label
    complexity_label: complexity_label
    text_label: text_label
    answer_label: answer_label
    back_btn: back
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
        Button:
            id: back
            text: "Назад"
            on_press:
                root._going_back()
''')


MAIN_MENU = 'main_menu'
GAME = 'game'
QUESTION = 'question'

DOMAIN = 'http://192.168.0.7'
API = {
    'start_game': urllib.request.urljoin(DOMAIN, 'game_mobile'),
    'get_question': urllib.request.urljoin(DOMAIN, 'questions'),
}


class Container(Screen):
    def __init__(self, **kw):
        super(Container, self).__init__(**kw)

    def start_game(self):
        change_screen('game')

    def add_question(self):
        pass


class GameScreen(Screen):

    def __init__(self, **kw):
        super(GameScreen, self).__init__(**kw)
        self.q_ids = []

    def show_q(self, _id):
        def show():
            change_screen(_id)
        return show

    def on_enter(self, **kw):
        app = App.get_running_app()

        if app.state == MAIN_MENU:
            app.state = GAME
            self.warning_label.text = ''
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
                        'on_press': self.show_q(q['_id']),
                        'q_id': q['_id']
                    }
                    sm.add_widget(Question(q))
                    self.questions.data.append(q_btn)
                    self.q_ids.append(q['_id'])
        elif app.state == QUESTION:
            app.state = GAME
            try:
                new_params = '.'.join(self.q_ids)
                request = urllib.request.urlopen(f'{API["get_question"]}?ids={new_params}')
            except (urllib.error.HTTPError, urllib.error.URLError):
                pass
            else:
                question = json.loads(request.read().decode("utf-8"))

                self.questions.data = [x for x in self.questions.data if x['q_id'] != app.current_q]

                if question.get('warning'):
                    self.warning_label.text = 'У нас закончились вопросы, но вы можете прислать свои, для других пользователей!'
                    return

                sm.add_widget(Question(question))
                _id = question['_id']
                q_btn = {
                    'text': question['text'],   
                    'valign': 'top',
                    'on_press': lambda: change_screen(_id),
                    'q_id': question['_id']
                }
                self.questions.data.append(q_btn)
                self.q_ids.append(question['_id'])

    def _going_back(self):

        app = App.get_running_app()
        app.state = MAIN_MENU
        change_screen(MAIN_MENU)


class Question(Screen):
    def __init__(self, question):
        super(Question, self).__init__()
        self.q = question
        self.name = question['_id']

    def on_enter(self):

        app = App.get_running_app()
        app.current_q = self.name
        app.state = QUESTION
        
        self.text_label.text = f'Вопрос: {self.q["text"]}'
        self.complexity_label.text = f'Сложность: {self.q["complexity"] * "*"}'
        self.category_label.text = f'Категория: {self.q["category"]}'
        self.answer_label.text = f'Ответ: {self.q["answer"]}'

    def _going_back(self):
        change_screen(GAME)


sm = ScreenManager()
sm.add_widget(Container(name='main_menu'))
sm.add_widget(GameScreen(name='game'))
sm.current = 'main_menu'


def change_screen(screen):
    sm.current = screen


class GameApp(App):

    def build(self):
        self.current_q = ''
        self.state = MAIN_MENU
        return sm

GameApp().run()
