"""
This file and all files contained within this distribution are parts of the SpeeDReaD speed reading program.

SpeeDReaD v.2.2.1
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
import threading
import time
from os.path import exists

from PyQt5.QtCore import QThread, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel

from GUI import GUI

class Main:
    settings = None

    def __init__(self):
        """
        Implements QThread to provide the ability to change the word(s) displayed in the reading area at the proper
        interval.
        :param GUI gui: The current instance of GUI
        """
        super().__init__()
        self.app = QApplication(sys.argv)

        self.current_word = 0
        self.keep_running = True
        self.wpm = 200
        self.reading_speed = None
        self.word_array = []

        thread = threading.Thread(target=self.load_settings)
        thread.start()
        thread.join()
        self.gui = GUI(self)
        self.apply_settings()

        self.gui.set_current_word_string.connect(self.gui.set_word)
        self.gui.set_word_slider_value.connect(self.gui.word_slider_set_value)

        sys.exit(self.app.exec())

    def start_reading(self):
        thread = threading.Thread(target=self.scroll_words)
        thread.start()

    def scroll_words(self):
        """
        Walks through the words in the user's text, applying the proper delay between words, and sends the word to the
        gui.
        :return: None
        """
        self.keep_running = True
        finished = False
        punctuations = ['.', ',', '?', '!', ';', '\uFF0C', '\u002C']

        skip_word = False
        initial_slowdown = True
        slowdown_value = 2
        for i in range(self.current_word, len(self.word_array)):
            if self.keep_running:
                if not skip_word:
                    word = self.word_array[i]
                    delay = self.reading_speed
                    if self.gui.punctuation_pause:
                        for punctuation in punctuations:
                            if punctuation in word:
                                delay = self.reading_speed * 1.5
                                break

                    if self.gui.group_words:
                        if len(word) < 4 or len(self.word_array[i + 1]) < 4:
                            word = word + ' ' + self.word_array[i + 1]
                            skip_word = True

                    self.gui.set_current_word_string.emit(word)
                    self.gui.set_word_slider_value.emit(i + 1)

                    if initial_slowdown:
                        time.sleep(delay * slowdown_value)
                        slowdown_value = slowdown_value - 0.05
                        if slowdown_value <= 1:
                            initial_slowdown = False
                    else:
                        time.sleep(delay)
                    self.current_word = i

                    if i == len(self.word_array) - 1:
                        finished = True
                else:
                    skip_word = False
            else:
                self.current_word = i
                if skip_word:
                    self.current_word -= 1
                self.calc_time_remaining()
                break

        if finished:
            time.sleep(2)
            self.current_word = 0
            self.set_current_word(self.current_word)
            self.gui.start_reading(True)

    def stop(self):
        """
        Convenience method to set self.keep_running to False, stopping the run loop
        :return:
        """
        self.keep_running = False

    def set_reading_speed(self, wpm, move_slider=False):
        """
        Method to set the reading speed based on the user's preference. Takes the value in Words Per Minute and converts
        that to a millisecond delay time, recalculating the read time remaining.
        :param wpm: Reading speed in Words Per Minute
        :param move_slider: Whether to also move the gui's speed slider
        :return:
        """
        self.wpm = wpm
        self.reading_speed = 60 / wpm
        self.calc_time_remaining()
        if move_slider:
            self.gui.speed_slider.setValue(wpm)

    def set_current_word(self, word_num):
        """
        Method to set the current word based on an index number. Uses signals to set the word being displayed in the gui
        and the word slider's value. Recalculates reading time remaining.
        :param word_num: Desired word's index
        :return:
        """
        self.current_word = word_num
        self.gui.set_word(self.word_array[self.current_word])
        self.gui.word_slider.setValue(word_num + 1)
        self.calc_time_remaining()

    def change_text(self, text, reset_current_word=True):
        """
        Cleans and sets the block of text to be read. Resets the current word index to 0.
        :param text: Text to be read
        :return:
        """
        text = re.sub("\u2014", "- ", text)
        text = re.sub("-", "- ", text)
        text = re.sub("\\s+", " ", text)
        text = re.sub("\r", "", text)
        text = re.sub("\n", "", text)
        text = re.sub("\t", "", text)

        self.word_array = text.strip().split(' ')

        self.gui.word_slider.setEnabled(True)
        self.gui.word_slider.setRange(1, len(self.word_array))
        self.gui.start_button.setEnabled(True)
        self.gui.stop_button.setEnabled(True)

        if reset_current_word:
            self.gui.set_word(self.word_array[0])
            self.set_current_word(0)

    def calc_time_remaining(self):
        """
        Method to calculate the time it will take to finish reading the text based on the current reading speed. Sets
        the time remaining label in GUI to the result.
        :return:
        """
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

            self.gui.time_remainting_set_text(result + ' remaining')

    def timed_popup(self, text):
        """
        Provides a popup showing the given text that will auto-close after one second.
        :param text: The desired text to be shown
        :return:
        """
        dialog = QWidget(self.gui)
        dialog.setStyleSheet('background-color: yellow')
        dialog.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        dialog.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        main_window_geometry = QApplication.primaryScreen().geometry()
        layout = QVBoxLayout()
        dialog.setLayout(layout)

        label = QLabel(text)
        label.setStyleSheet('color: red')
        label.setFont(QFont('Arial-Bold', 16))
        layout.addWidget(label)
        dialog.adjustSize()

        dialog.setGeometry(
            int(main_window_geometry.width() / 2) - int(dialog.width() / 2),
            int(main_window_geometry.height() / 2) - int(dialog.width() / 2),
            dialog.width(),
            dialog.height()
        )

        dialog.show()
        now_time = time.time()
        while time.time() < now_time + 2:
            if self.app.hasPendingEvents():
                self.app.processEvents()
            time.sleep(0.1)
        dialog.deleteLater()

    def load_settings(self):
        """
        Method to retrieve the user's saved settings from the settings file.
        :return:
        """
        if 'linux' in sys.platform:
            data_dir = os.path.expanduser('~/.config/SpeeDReaD')
        else:
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
        """
        Method to save the current settings to the user's settings file.
        :return:
        """
        self.settings['speed'] = self.wpm
        self.settings['current_word'] = self.current_word
        self.settings['font_name'] = self.gui.current_font.family()
        self.settings['font_size'] = self.gui.current_font.pointSize()
        self.settings['background'] = self.gui.current_background
        self.settings['pause'] = self.gui.punctuation_pause
        self.settings['combine'] = self.gui.group_words
        if self.word_array:
            self.settings['reading_text'] = ' '.join(self.word_array)
        else:
            self.settings['reading_text'] = None

        if 'linux' in sys.platform:
            data_dir = os.path.expanduser('~/.config/SpeeDReaD')
        else:
            data_dir = os.getenv('APPDATA') + '/SpeeDReaD'
        settings_file = data_dir + '/settings.json'

        with open(settings_file, 'w') as file:
            file.write(json.dumps(self.settings, indent=2))

    def apply_settings(self):
        """
        Method to take the current settings and apply them to the program
        :return:
        """
        if self.settings['reading_text'] and len(self.settings['reading_text'].strip()) > 0:
            self.change_text(self.settings['reading_text'], False)
            self.gui.reading_ready_widget_set(len(self.settings['reading_text'].split(' ')))

        self.wpm = self.settings['speed']
        self.set_reading_speed(self.settings['speed'])
        self.gui.speed_slider.setValue(self.wpm)

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

        if not self.settings['speed']:
            self.settings['speed'] = 200
        self.gui.speed_slider.setValue(self.settings['speed'])
        self.set_reading_speed(self.settings['speed'])

        if self.settings['current_word']:
            self.set_current_word(self.settings['current_word'])
        else:
            self.current_word = 0


if __name__ == '__main__':
    """
    Main entry point
    """
    speed_read = Main()

