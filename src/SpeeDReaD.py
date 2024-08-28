"""
This file and all files contained within this distribution are parts of the SpeeDReaD speed reading program.

SpeeDReaD v.2.1.1
Written by Jeremy G Wilson

ProjectOn is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License (GNU GPL)
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import json
import os.path
import re
import sys
import time
from os.path import exists

from PyQt5.QtCore import QThread, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel

from GUI import GUI

class SpeedRead(QThread):
    settings = None

    def __init__(self, gui):
        """
        Implements QThread to provide the ability to change the word(s) displayed in the reading area at the proper
        interval.
        :param GUI gui: The current instance of GUI
        """
        self.load_settings()
        self.gui = gui
        self.current_word = 0
        self.keep_running = True
        self.wpm = 200
        self.reading_speed = None
        self.word_array = None

        super().__init__()

    def run(self):
        self.keep_running = True
        finished = False
        punctuations = ['.', ',', '?', '!', ';', '\uFF0C', '\u002C']

        skip_word = False
        initial_slowdown = True
        slowdown_value = 2
        for i in range(self.current_word, len(self.word_array)):
            if slowdown_value <= 1:
                initial_slowdown = False

            if not skip_word:
                delay = self.reading_speed

            if self.keep_running:
                if not skip_word:
                    if len(self.word_array[i]) < 4 and self.gui.group_words and not i == len(self.word_array) - 1:
                        word = self.word_array[i] + ' ' + self.word_array[i + 1]
                        skip_word = True
                    else:
                        word = self.word_array[i]

                    delay = self.reading_speed
                    if self.gui.punctuation_pause:
                        for punctuation in punctuations:
                            if punctuation in word:
                                delay = self.reading_speed * 2

                    self.gui.word_label.setText(word)
                    self.gui.word_slider.blockSignals(True)
                    self.gui.word_slider.setValue(i + 1)
                    self.gui.word_slider.blockSignals(False)
                    app.processEvents()

                    if initial_slowdown:
                        time.sleep(delay * slowdown_value)
                        slowdown_value = slowdown_value - 0.05
                    else:
                        time.sleep(delay)
                    self.current_word = i
                else:
                    skip_word = False
                    self.gui.word_slider.blockSignals(True)
                    self.gui.word_slider.setValue(i + 1)
                    self.gui.word_slider.blockSignals(False)

                if i == len(self.word_array) - 1:
                    finished = True
            else:
                self.current_word = i
                self.calc_time_remaining()
                break

        if finished:
            time.sleep(2)
            self.current_word = 0
            self.gui.word_label.setText(self.word_array[0])
            self.gui.word_slider.setValue(1)

    def stop(self):
        self.keep_running = False

    def set_reading_speed(self, wpm, move_slider=False):
        self.wpm = wpm
        self.reading_speed = 60 / wpm
        self.calc_time_remaining()
        if move_slider:
            self.gui.speed_slider.setValue(wpm)

    def set_current_word(self, word_num):
        self.current_word = word_num
        self.gui.word_label.setText(self.word_array[self.current_word])
        self.gui.word_slider.setValue(word_num + 1)
        self.calc_time_remaining()

    def change_text(self, text):
        text = re.sub("\u2014", "- ", text)
        text = re.sub("-", "- ", text)
        text = re.sub("\\s+", " ", text)
        text = re.sub("\r", "", text)
        text = re.sub("\n", "", text)
        text = re.sub("\t", "", text)

        self.word_array = text.strip().split(' ')
        self.set_current_word(0)
        self.gui.word_label.setText(self.word_array[0])
        self.gui.word_slider.setValue(1)

    def calc_time_remaining(self):
        if self.word_array:
            num_words = len(self.word_array) - self.current_word
            time_left = num_words / self.gui.speed_slider.value()

            hours = 0
            minutes = 0
            seconds = 0
            if time_left > 60:
                seconds = int((time_left % 1) * 60)
                time_left = time_left - (time_left % 1)
                minutes = int(time_left % 60)
                hours = int((time_left - minutes) / 60)
            elif time_left > 1:
                seconds = int((time_left % 1) * 60)
                minutes = int(time_left - (time_left % 1))
            elif time_left < 1:
                seconds = int(time_left * 60)

            if hours < 1 and minutes < 1:
                result = 'less than 1 minute'
            else:
                result = str(hours) + ':' + str(minutes) + ':' + str(seconds)

            self.gui.time_remaining_label.setText(result + ' remaining')

    def timed_popup(self, text):
        dialog = QWidget()
        dialog.setStyleSheet('background-color: yellow')
        dialog.setWindowFlag(Qt.FramelessWindowHint)
        dialog.setGeometry(10, 20, 0, 20)
        layout = QVBoxLayout()
        dialog.setLayout(layout)

        label = QLabel(text)
        label.setStyleSheet('color: red')
        label.setFont(QFont('Arial-Bold', 16))
        layout.addWidget(label)

        dialog.show()
        app.processEvents()
        time.sleep(1.0)
        dialog.destroy()

    def load_settings(self):
        data_dir = os.getenv('APPDATA') + '/SpeeDReaD'
        settings_file = data_dir + '/settings.json'

        if not exists(data_dir):
            os.mkdir(data_dir)

        if exists(settings_file):
            with open(settings_file, 'r') as file:
                self.settings = json.loads(file.read())
        else:
            self.settings = {
                'speed': 200,
                'current_word': None,
                'font_name': 'Arial',
                'font_size': 36,
                'background': 'white',
                'pause': True,
                'combine': True,
                'reading_text': ''
            }
            with open(settings_file, 'w') as file:
                file.write(json.dumps(self.settings, indent=2))

    def save_settings(self):
        self.settings.update({'speed': self.wpm})
        self.settings.update({'current_word': self.current_word})
        self.settings.update({'font_name': self.gui.current_font.family()})
        self.settings.update({'font_size': self.gui.current_font.pointSize()})
        self.settings.update({'background': self.gui.current_background})
        self.settings.update({'pause': self.gui.punctuation_pause})
        self.settings.update({'combine': self.gui.group_words})
        if self.word_array:
            self.settings.update({'reading_text': ' '.join(self.word_array)})
        else:
            self.settings.update({'reading_text': None})

        data_dir = os.getenv('APPDATA') + '/SpeeDReaD'
        settings_file = data_dir + '/settings.json'

        with open(settings_file, 'w') as file:
            file.write(json.dumps(self.settings, indent=2))

    def apply_settings(self):
        if self.settings['reading_text'] and len(self.settings['reading_text']) > 0:
            self.change_text(self.settings['reading_text'])
            self.gui.word_slider.setEnabled(True)
            self.gui.word_slider.setRange(1, len(self.settings['reading_text'].split(' ')))
            self.gui.start_button.setEnabled(True)
            self.gui.stop_button.setEnabled(True)

        self.wpm = self.settings['speed']
        self.set_reading_speed(self.settings['speed'])
        self.gui.speed_slider.setValue(self.wpm)

        if self.settings['current_word']:
            self.set_current_word(self.settings['current_word'])
        else:
            self.current_word = 0

        self.gui.current_font = QFont(self.settings['font_name'], self.settings['font_size'])
        self.gui.word_label.setFont(self.gui.current_font)
        self.gui.change_background(self.settings['background'])

        self.gui.punctuation_pause = self.settings['pause']
        if self.settings['pause']:
            self.gui.options_menu.pause_punctuation_action.setIcon(self.gui.icons['punctuation_on'])
        else:
            self.gui.options_menu.pause_punctuation_action.setIcon(self.gui.icons['punctuation_off'])

        self.gui.group_words = self.settings['combine']
        if self.settings['combine']:
            self.gui.options_menu.group_words_action.setIcon(self.gui.icons['combine_on'])
        else:
            self.gui.options_menu.group_words_action.setIcon(self.gui.icons['combine_off'])

class Startup:
    def __init__(self):
        gui = GUI()

        speed_read = SpeedRead(gui)

        gui.set_reading_speed.connect(speed_read.set_reading_speed)
        gui.start_words.connect(speed_read.start)
        gui.stop_words.connect(speed_read.stop)
        gui.set_current_word.connect(speed_read.set_current_word)
        gui.change_text.connect(speed_read.change_text)
        gui.save_settings.connect(speed_read.save_settings)
        gui.timed_popup.connect(speed_read.timed_popup)

        speed_read.apply_settings()
        gui.showMaximized()
        app.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    startup = Startup()

