import ebooklib
import os.path
import re
import time

from codecs import decode
from ebooklib import epub
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QMainWindow, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QSlider, \
    QDialog, QTextEdit, QFontDialog, QTabWidget, QTextBrowser, QGridLayout, QFileDialog

from OptionsMenu import OptionsMenu


class GUI(QMainWindow):
    set_reading_speed = pyqtSignal(int)
    start_words = pyqtSignal()
    stop_words = pyqtSignal()
    set_current_word_index = pyqtSignal(int)
    set_current_word_string = pyqtSignal(str)
    change_text = pyqtSignal(str)
    save_settings = pyqtSignal()
    timed_popup = pyqtSignal(str)
    block_word_slider_signals = pyqtSignal(bool)
    set_word_slider_value = pyqtSignal(int)

    current_font = None
    punctuation_pause = None
    group_words = None
    current_background = None

    def __init__(self):
        super().__init__()
        os.chdir(os.path.dirname(__file__))

        self.icons = {
            'window': QIcon('resources/sr_logo.svg'),
            'edit': QIcon('resources/edit.svg'),
            'play': QIcon('resources/play.svg'),
            'stop': QIcon('resources/stop.svg'),
            'settings': QIcon('resources/settings.svg'),
            'font': QIcon('resources/change_font.svg'),
            'background': QIcon('resources/change_background.svg'),
            'punctuation_off': QIcon('resources/punctuation.svg'),
            'punctuation_on': QIcon('resources/punctuation_grey.svg'),
            'combine_off': QIcon('resources/combine.svg'),
            'combine_on': QIcon('resources/combine_grey.svg')
        }
        self.create_gui()
        self.setWindowTitle('SpeeDReaD')
        self.setWindowIcon(self.icons['window'])

    def create_gui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.setContentsMargins(0, 0, 0, 0)
        main_widget.setContentsMargins(0, 0, 0, 0)

        self.word_widget = QWidget()
        word_layout = QVBoxLayout()
        self.word_widget.setLayout(word_layout)

        self.word_label = QLabel('SpeeDReaD')
        self.word_label.setAlignment(Qt.AlignCenter)
        word_layout.addStretch()
        word_layout.addWidget(self.word_label)
        word_layout.addStretch()

        main_layout.addWidget(self.word_widget)

        slider_container = QWidget()
        slider_layout = QHBoxLayout()
        slider_layout.setContentsMargins(50, 10, 50, 10)
        slider_container.setLayout(slider_layout)
        slider_container.setStyleSheet('background-color: white')

        self.word_slider = QSlider()
        self.word_slider.setOrientation(Qt.Horizontal)
        self.word_slider.setAutoFillBackground(False)
        self.word_slider.setFocusPolicy(Qt.NoFocus)
        self.word_slider.valueChanged.connect(self.slider_word_change)
        self.word_slider.setToolTip('Drag to change current word')
        slider_layout.addWidget(self.word_slider)
        main_layout.addWidget(slider_container)
        self.word_slider.setEnabled(False)

        button_widget = QWidget()
        button_widget.setObjectName('button_widget')
        button_widget.setStyleSheet('#button_widget { background-color: #F0F0FF; border-top: 1px solid #A0A0FF}')
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(50, 10, 50, 10)
        button_widget.setLayout(button_layout)

        self.speed_slider = QSlider()
        self.speed_slider.setRange(100, 999)
        self.speed_slider.setValue(200)
        self.speed_slider.setSingleStep(10)
        self.speed_slider.setFocusPolicy(Qt.NoFocus)
        self.speed_slider.setOrientation(Qt.Horizontal)
        self.speed_slider.setFixedWidth(200)
        self.speed_slider.setToolTip('Reading speed (in words per minute)')
        self.speed_slider.valueChanged.connect(self.change_speed)
        button_layout.addWidget(self.speed_slider)

        speed_widget = QWidget()
        speed_layout = QVBoxLayout()
        speed_layout.setContentsMargins(10, 0, 0, 0)
        speed_widget.setLayout(speed_layout)

        self.speed_label = QLabel('200 wpm')
        speed_layout.addWidget(self.speed_label)

        self.time_remaining_label = QLabel()
        speed_layout.addWidget(self.time_remaining_label)
        button_layout.addWidget(speed_widget)

        load_button = QPushButton()
        load_button.setIcon(self.icons['edit'])
        load_button.setStyleSheet(
            'QPushButton { background-color: #F0F0FF; border: none; }' +
            'QPushButton:hover { background-color: lightgrey; border: none; }'
        )
        load_button.setFocusPolicy(Qt.NoFocus)
        load_button.setIconSize(QSize(32, 32))
        load_button.setToolTip('Paste or import text to read')
        load_button.pressed.connect(self.load_text)
        button_layout.addWidget(load_button)
        button_layout.addStretch()

        self.start_button = QPushButton()
        self.start_button.setIcon(self.icons['play'])
        self.start_button.setStyleSheet(
            'QPushButton { background-color: #F0F0FF; border: none; }' +
            'QPushButton:hover { background-color: lightgrey; border: none; }' +
            'QPushButton:checked { background-color: lightgrey; border: none; }'
        )
        self.start_button.setFocusPolicy(Qt.NoFocus)
        self.start_button.setIconSize(QSize(32, 32))
        self.start_button.setToolTip('Start or Pause reading')
        self.start_button.setCheckable(True)
        self.start_button.pressed.connect(self.start_reading)
        self.start_button.setEnabled(False)
        button_layout.addWidget(self.start_button)
        button_layout.addSpacing(20)

        self.stop_button = QPushButton()
        self.stop_button.setIcon(self.icons['stop'])
        self.stop_button.setStyleSheet(
            'QPushButton { background-color: #F0F0FF; border: none; }' +
            'QPushButton:hover { background-color: lightgrey; border: none; }'
        )
        self.stop_button.setFocusPolicy(Qt.NoFocus)
        self.stop_button.setIconSize(QSize(32, 32))
        self.stop_button.setToolTip('Stop and return to the first word')
        self.stop_button.pressed.connect(self.reset)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        button_layout.addSpacing(250) # get the start and stop buttons closer to the center
        button_layout.addStretch()

        self.options_button = QPushButton()
        self.options_button.setIcon(self.icons['settings'])
        self.options_button.setStyleSheet(
            'QPushButton { background-color: #F0F0FF; border: none; }' +
            'QPushButton:hover { background-color: lightgrey; border: none; }'
        )
        self.options_button.setFocusPolicy(Qt.NoFocus)
        self.options_button.setIconSize(QSize(32, 32))
        self.options_button.setToolTip('Options')
        button_layout.addWidget(self.options_button)

        self.options_menu = OptionsMenu(self)
        self.options_button.setMenu(self.options_menu)

        main_layout.addWidget(button_widget)

    def slider_word_change(self):
        self.set_current_word_index.emit(self.sender().value() - 1)

    def word_slider_block_signals(self, value):
        self.word_slider.blockSignals(value)

    def word_slider_set_value(self, index):
        self.word_slider.blockSignals(True)
        self.word_slider.setValue(index)
        self.word_slider_block_signals(False)

    def set_word(self, word):
        self.word_label.setText(word)

    def change_background(self, color):
        self.current_background = color
        if color == 'white':
            self.word_widget.setStyleSheet('background-color: white')
            self.word_label.setStyleSheet('font-color: black')
        elif color == 'cream':
            self.word_widget.setStyleSheet('background-color: #EFE0D0')
            self.word_label.setStyleSheet('font-color: black')
        elif color == 'neutral':
            self.word_widget.setStyleSheet('background-color: #B0B0B0')
            self.word_label.setStyleSheet('font-color: black')
        elif color == 'black':
            self.word_widget.setStyleSheet('background-color: black')
            self.word_label.setStyleSheet('color: white')

    def pause_for_punctuation(self):
        if self.punctuation_pause:
            self.punctuation_pause = False
            self.options_menu.pause_punctuation_action.setIcon(self.icons['punctuation_off'])
            self.timed_popup.emit('Punctuation Pause OFF')
        else:
            self.punctuation_pause = True
            self.options_menu.pause_punctuation_action.setIcon(self.icons['punctuation_on'])
            self.timed_popup.emit('Punctuation Pause ON')

    def combine_words(self):
        if self.group_words:
            self.group_words = False
            self.options_menu.group_words_action.setIcon(self.icons['combine_off'])
            self.timed_popup.emit('Combine Small Words OFF')
        else:
            self.group_words = True
            self.options_menu.group_words_action.setIcon(self.icons['combine_on'])
            self.timed_popup.emit('Combine Small Words ON')

    def change_speed(self):
        value = self.sender().value()
        self.speed_label.setText(str(value) + ' wpm')
        self.set_reading_speed.emit(value)

    def change_font(self):
        font_dialog = QFontDialog()
        result = font_dialog.getFont(self.current_font, self, 'Choose Reading Font')

        if result[1]:
            self.current_font = result[0]
            self.word_label.setFont(self.current_font)

    def start_reading(self, set_state=False):
        if self.start_button.isChecked():
            self.stop_words.emit()
            if set_state:
                self.start_button.setChecked(False)
        else:
            self.start_words.emit()
            if set_state:
                self.start_button.setChecked(True)

    def reset(self):
        if self.start_button.isChecked():
            self.stop_words.emit()
            self.start_button.setChecked(False)
        time.sleep(0.3)
        self.set_current_word_index.emit(0)

    def load_text(self):
        dialog = QDialog()
        dialog.setModal(True)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        dialog.setLayout(layout)

        label = QLabel('Paste text here:')
        layout.addWidget(label)

        text_edit = QTextEdit()
        layout.addWidget(text_edit)

        button_widget = QWidget()
        button_layout = QHBoxLayout()
        button_widget.setLayout(button_layout)

        ok_button = QPushButton('OK')
        ok_button.pressed.connect(lambda: dialog.done(0))
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addSpacing(20)

        cancel_button = QPushButton('Cancel')
        cancel_button.pressed.connect(lambda: dialog.done(1))
        button_layout.addWidget(cancel_button)

        layout.addWidget(button_widget)
        button_layout.addStretch()

        or_label = QLabel('OR')
        or_label.setFont(QFont('Arial', 16))
        or_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(or_label)

        import_button = QPushButton('Import from EPUB')
        import_button.setStyleSheet('padding: 10px;')
        import_button.pressed.connect(lambda: dialog.done(2))
        layout.addWidget(import_button, 0, Qt.AlignCenter)

        result = dialog.exec()
        if result == 0:
            self.change_text.emit(text_edit.toPlainText())
            self.word_slider.setEnabled(True)
            self.word_slider.setRange(1, len(text_edit.toPlainText().split(' ')))
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(True)
        elif result == 2:
            file_dialog = QFileDialog()
            result = file_dialog.getOpenFileName(
                self,
                'Import from EPUB',
                os.path.expanduser('~') + '/Documents',
                'EPUB (*.epub)'
            )

            if len(result[0]) > 0:
                if '.epub' in result[0]:
                    book = epub.read_epub(result[0])

                    text_array = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)

                    all_text = ''
                    for text in text_array:
                        text = decode(text.get_body_content(), 'utf-8')
                        text = text.replace('</p>', ' ')
                        text = re.sub('<.*?>', '', text)
                        text = re.sub('\n+', ' ', text)
                        if len(text.strip()) > 0:
                            all_text += ' ' + text.strip()

                    self.change_text.emit(all_text)
                    self.word_slider.setEnabled(True)
                    self.word_slider.setRange(1, len(all_text.split(' ')))
                    self.start_button.setEnabled(True)
                    self.stop_button.setEnabled(True)

    def show_help(self):
        title_font = QFont('Arial-Bold', 24)
        regular_font = QFont('Arial', 12)

        self.help_widget = QTabWidget()
        self.help_widget.setFixedSize(800, 500)
        self.help_widget.setFont(QFont('Arial-Bold', 16))

        hotkeys_widget = QWidget()
        help_layout = QVBoxLayout()
        hotkeys_widget.setLayout(help_layout)
        help_layout.addSpacing(20)

        container = QWidget()
        container_layout = QGridLayout()
        container.setLayout(container_layout)

        logo_label = QLabel()
        logo_label.setPixmap(QPixmap('resources/sr_logo.svg'))
        container_layout.addWidget(logo_label, 0, 0, 2, 1, Qt.AlignTop)

        help_title = QLabel('SpeeDReaD')
        help_title.setFont(title_font)
        container_layout.addWidget(help_title, 0, 1)

        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setStyleSheet('background: none; border: none;')
        help_text.setFont(regular_font)
        help_text.setText('SpeeDReaD (pronounced Speedy Read-y) is a program to help you read faster. By flashing the'
                          'individual words of what you want to read on a single spot on your screen, you avoid both '
                          'the rapid eye movements and the internal sounding-out of the words that can slow you down. '
                          'In a short time, you will be able to increase your reading speed greatly.\n\n See below '
                          'for the hotkeys you can use with the program.')
        container_layout.addWidget(help_text, 1, 1)
        help_layout.addWidget(container)

        hotkeys_title = QLabel('Hotkeys')
        hotkeys_title.setFont(title_font)
        help_layout.addWidget(hotkeys_title)

        hotkeys_text = QTextEdit()
        hotkeys_text.setReadOnly(True)
        hotkeys_text.setStyleSheet('background: none; border: none;')
        hotkeys_text.setFont(regular_font)
        hotkeys_text.setText('CTRL-R: Start/Pause Reading\nCTRL-UP: Increase Reading Speed\nCTRL-DOWN: Decrease'
                             'Reading Speed\nCTRL-LEFT: Go to the previous word\nCTRL-RIGHT: Go to the next word'
                             '\nBACKSPACE: Stop, reset to the first word')
        help_layout.addWidget(hotkeys_text)
        help_layout.addStretch()

        self.help_widget.addTab(hotkeys_widget, 'SpeeDReaD')

        about_widget = QWidget()
        about_layout = QVBoxLayout()
        about_widget.setLayout(about_layout)

        about_text = QTextBrowser()
        about_text.setHtml('''
                    SpeeDReaD is free software: you can redistribute it and/or
                    modify it under the terms of the GNU General Public License (GNU GPL)
                    published by the Free Software Foundation, either version 3 of the
                    License, or (at your option) any later version.<br><br>

                    This program is distributed in the hope that it will be useful,
                    but WITHOUT ANY WARRANTY; without even the implied warranty of
                    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                    GNU General Public License for more details.<br><br>

                    You should have received a copy of the GNU General Public License
                    along with this program. If not, see 
                    <a href="http://www.gnu.org/licenses/">http://www.gnu.org/licenses/</a>.<br><br>
                ''')
        about_text.setStyleSheet('font-family: "Helvetica"; font-size: 16px')
        about_text.setOpenExternalLinks(True)
        about_text.setReadOnly(True)
        about_layout.addWidget(about_text)

        self.help_widget.addTab(about_widget, 'About')

        self.help_widget.show()

    def keyPressEvent(self, evt):
        if evt.modifiers and Qt.ControlModifier:
            if evt.key() == Qt.Key_R:
                if self.start_button.isEnabled():
                    self.start_reading(True)
            if evt.key() == Qt.Key_Up:
                self.speed_slider.setValue(self.speed_slider.value() + 10)
            if evt.key() == Qt.Key_Down:
                self.speed_slider.setValue(self.speed_slider.value() - 10)
            if evt.key() == Qt.Key_Left:
                if self.start_button.isEnabled():
                    self.word_slider.setValue(self.word_slider.value() - 1)
            if evt.key() == Qt.Key_Right:
                if self.start_button.isEnabled():
                    self.word_slider.setValue(self.word_slider.value() + 1)
        if evt.key() == Qt.Key_Backspace:
            if self.start_button.isEnabled():
                self.reset()

    def closeEvent(self, evt):
        self.save_settings.emit()
        evt.accept()
