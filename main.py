import kivy
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty
import psycopg2
import pendulum
import datetime
import argparse


Window.clearcolor = (0.5, 0.5, 0.5, 1)
Window.size = (400, 300)



local_tz = pendulum.timezone("Europe/Warsaw")
conn_source = psycopg2.connect(host="", database="timeregistry", user="admin",
                        password="")


class MainWindow(Screen):
    card = ObjectProperty(None)
    # eventName = StringProperty('') #TODO: make 'event' a global var

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.event = ''
        Window.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if self.card.focus and keycode == 40:
            self.submit_stuff()
        return self.__init__

    def submit_stuff(self):
        cur = conn_source.cursor()
        card = self.card.text
        sql_new = """insert into register_timeregister(card, "TimeStampIn", "TimeStampOut", uploaded)
                        values(%s, %s, %s, %s) returning card;"""
        cur.execute("""select id, card, "TimeStampIn", "TimeStampOut" from register_timeregister where card = '{0}' and "TimeStampIn" >= NOW() - '11 hour'::INTERVAL ORDER BY "TimeStampIn" DESC limit 1"""
                   .format(card),
                 ("card", card)
                 )
        answer = cur.fetchone()
        if answer:
            if list(answer)[3]:
                cur.execute(sql_new, (card, datetime.datetime.now(), None, False))
                conn_source.commit()
                # print(list(answer)[0], list(answer)[1], list(answer)[2], list(answer)[3]) # create new -> entry
                self.event = 'entry'
            else:
                update_id = list(answer)[0]
                leaving_time = str(datetime.datetime.now())
                cur.execute(
                    """update register_timeregister set "TimeStampOut" = '{0}' where id='{1}'"""
                    .format(leaving_time, update_id), (('leaving_time', leaving_time), ('update_id', update_id))
                )
                conn_source.commit()
                self.event = 'leave'
        else:
            cur.execute(sql_new, (card, datetime.datetime.now(), None, False))
            conn_source.commit()
            self.event  = 'entry new'
        cur.close()
        # global event
        # event = eventName
        # print(self.event)
        self.card.text = ""
        self.card.focus = True
        self.changeScreen()
        return self.__init__

    def changeScreen(self):
        print(self.event)
        if self.manager.current == 'main':
            self.manager.current = 'second'
            self.manager.transition.direction = 'left'
        else:
            self.manager.current = 'main'
            self.manager.transition.direction = 'right'


class SecondWindow(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class MyApp(App):
    def build(self):
        return self.root

if __name__ == "__main__":
    MyApp().run()