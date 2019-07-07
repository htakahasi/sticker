# -*- coding: utf-8 -*-

from kivy.app import App
# from kivy.graphics import Color
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.config import Config
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path
from kivy.utils import platform
from setting import corners
import random
import threading
import time


class Floor:

    def __init__(self, name, start, matrix):
        self.name = name
        self.matrix = matrix
        self.start = start
        self.mapping = self.gen_map(matrix, start)
        self.dictionary = self.gen_dic(matrix, start)

    def gen_map(self, matrix, start):
        """ Generate floor matrix map.
        """
        whole_map = []
        block = []

        for x in matrix:
            if 'backward' == x[2]:
                block = [[start + m * x[0] + n for n in range(x[0], 0, -1)]
                         for m in range(0, x[1])]
            elif 'forward' == x[2]:
                block = [[start + m * x[0] + n for n in range(1, x[0] + 1)]
                         for m in range(0, x[1])]
            elif 'split' == x[2]:
                for m in range(0, x[1]):
                    block.append([start + m * x[0] + n
                                  for n in range(1, x[0] // 2 + 1)])
                    block.append([start + m * x[0] + n
                                  for n in range(x[0], x[0] // 2, -1)])
            else:
                raise TypeError('Illegal sequence specifier')
            whole_map = whole_map + block
            start = max(max(block))
        return whole_map

    def gen_dic(self, matrix, start):
        """ Generate store dictionary.
        """
        whole_dic = []
        block = []

        for x in matrix:
            if 'backward' == x[2]:
                block = [(start + m * x[0] + n,
                          str(x[0]) + 'b' + str(x[0] - n + 1))
                         for n in range(x[0], 0, -1)
                         for m in range(0, x[1])]
            elif 'forward' == x[2]:
                block = [(start + m * x[0] + n,
                          str(x[0]) + 'f' + str(n))
                         for n in range(1, x[0] + 1)
                         for m in range(0, x[1])]
            elif 'split' == x[2]:
                for m in range(0, x[1]):
                    block = block + [(start + m * x[0] + n,
                                      str(x[0] // 2) + 'f' + str(n))
                                     for n in range(1, x[0] // 2 + 1)]
                    block = block + [(start + m * x[0] + n,
                                      str(x[0] // 2) + 'b' + str(x[0] - n + 1))
                                     for n in range(x[0], x[0] // 2, -1)]
            else:
                raise TypeError('Illegal sequence specifier')
            whole_dic = whole_dic + block
            start = max(block)[0]
        return whole_dic


def floor_dic():
    """ Generate dictionary of whole parking addresses
    """
    whole_dic = []
    for i in corners:
        n = Floor(name=i[0], start=i[2], matrix=i[3])
        whole_dic = whole_dic + n.dictionary
        dic = dict(whole_dic)
    return dic


def set_regular(family, *filenames):
    for f in filenames:
        try:
            LabelBase.register(family, f)
            break
        except IOError:
            continue
    else:
        raise IOError('No appropriate fonts for Kivy UI')


# ここからkivy NUI
if platform == 'android':
    resource_add_path('/system/fonts/')
    set_regular(DEFAULT_FONT,
                'DroidSansJapanese.ttf',
                'MTLmr3m.ttf',
                'MTLc3m.ttf',
                'NotoSansJP-Regular.otf',
                'SomcUDGothic-Regular.ttf',
                'LCMincho.ttf',
                'DroidSansFallback.ttf')
else:
    Config.set('graphics', 'width', '480')
    Config.set('graphics', 'height', '854')

    resource_add_path('/Users/user/Library/Fonts')
    LabelBase.register(DEFAULT_FONT, 'NotoSansCJKjp-Thin.otf')


class Sticker(BoxLayout):
    placeString = StringProperty()
    question = NumericProperty()
    resultString = StringProperty()
    dismissString = StringProperty()
    remainTimeString = StringProperty()
    remainTimeColor = ListProperty()
    score = NumericProperty()

    def __init__(self, **kwargs):
        super(Sticker, self).__init__(**kwargs)
        self.placeString = '指定なし'
        self.daioki = 1
        self.daiokiString = ''
        self.tome = 'f'
        self.tomeString = ''
        self.daime = 1
        self.daimeString = ''
        self.answer = ''
        self.dic = floor_dic()
        self.question = random.choice(list(self.dic.keys()))
        self.questionString = str(self.question)
        self.toan = ''
        self.resultString = ''
        self.correct_answer = self.dic[self.question]
        self.dismissString = '決定'
        self.remainTimeColor = [1, 1, 1, 1]
        self.score = 0

    def daiokiTapped(self, n):
        self.daioki = n
        self.daiokiString = '%d台置き' % n
        self.placeString = self.daiokiString + ' ' + self.tomeString + \
            ' ' + self.daimeString
        self.toan = str(self.daioki) + self.tome + str(self.daime)

    def directionTapped(self, d):
        if 'forward' == d:
            self.tome = 'f'
            self.tomeString = '前停め'
        elif 'backward' == d:
            self.tome = 'b'
            self.tomeString = 'バック停め'
        else:
            self.tome = ''
            self.tomeString = ''
        self.placeString = self.daiokiString + ' ' + self.tomeString + \
            ' ' + self.daimeString
        self.toan = str(self.daioki) + self.tome + str(self.daime)

    def daimeTapped(self, n):
        self.daime = n
        self.daimeString = '%d台目' % n
        self.placeString = self.daiokiString + ' ' + self.tomeString + \
            ' ' + self.daimeString
        self.toan = str(self.daioki) + self.tome + str(self.daime)

    def ketteiTapped(self):
        if '決定' == self.dismissString:
            if self.toan == self.correct_answer:
                self.resultString = '正解!'
                self.score += 1
                self.dismissString = '次'
            else:
                self.resultString = '不正解!'
        else:
            self.dismissString = '決定'
            self.question = random.choice(list(self.dic.keys()))
            self.questionString = str(self.question)
            self.toan = ''
            self.resultString = ''
            self.correct_answer = self.dic[self.question]


# タイマー
class StickerTimer:
    """ 1秒ごとに残り時間を表示するタイマー
    """

    def __init__(self, t, sticker):
        self.timer = t
        self.sub_t = None
        self.start_time = time.time()
        self.sticker = sticker

    def continuous_timer(self):
        self.now = self.timer - (time.time() - self.start_time)
        self.sticker.remainTimeString = '(残り時間…' +\
            '%.2d' % (self.now // 60) +\
            ':' + '%.2d)' % (self.now % 60)
        if 10 > self.now:
            self.sticker.remainTimeColor = [1, 0, 0, 1]
        self.sub_t = threading.Timer(1, self.continuous_timer)
        self.sub_t.start()


class StickerApp(App):
    def __init__(self, **kwargs):
        super(StickerApp, self).__init__(**kwargs)

    def build(self):
        self.sticker = Sticker()
        sticker_timer_limit = 180

        self.mt = threading.Timer(sticker_timer_limit, self.halt_message)
        self.mt.start()

        self.st = StickerTimer(sticker_timer_limit, self.sticker)
        self.st.continuous_timer()

        return self.sticker

    def cancel_timers(self):
        self.mt.cancel()
        self.st.sub_t.cancel()

    def halt_message(self):
        self.cancel_timers()
        popup = Popup(title='終了しました',
                      content=Label(text='時間切れです(%.3d点)' %
                                    self.sticker.score),
                      size_hint=(None, None),
                      size=(300, 300))
        popup.bind(on_dismiss=self.stop)
        popup.open()


if __name__ == '__main__':
    StickerApp().run()
