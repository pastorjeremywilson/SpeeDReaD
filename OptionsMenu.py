from PyQt5.QtWidgets import QMenu, QAction


class OptionsMenu(QMenu):
    def __init__(self, gui):
        """
        Implements QMenu to provide a popup menu for the settings button in GUI
        :param GUI gui: The current instance of GUI
        """
        self.gui = gui
        super().__init__()
        self.create_menu()

    def create_menu(self):
        """
        Method to add all of the actions to this menu
        :return:
        """
        change_font_action = QAction(self.gui.options_button)
        change_font_action.setIcon(self.gui.icons['font'])
        change_font_action.setText('&Change Font')
        change_font_action.triggered.connect(self.gui.change_font)
        self.addAction(change_font_action)

        change_background_menu = self.addMenu('Change Background')
        change_background_menu.setIcon(self.gui.icons['background'])
        self.addMenu(change_background_menu)

        background_white_action = QAction(self.gui.options_button)
        background_white_action.setText('&White')
        background_white_action.triggered.connect(lambda: self.gui.change_background('white'))
        change_background_menu.addAction(background_white_action)

        background_cream_action = QAction(self.gui.options_button)
        background_cream_action.setText('&Cream')
        background_cream_action.triggered.connect(lambda: self.gui.change_background('cream'))
        change_background_menu.addAction(background_cream_action)

        background_neutral_action = QAction(self.gui.options_button)
        background_neutral_action.setText('&Neutral')
        background_neutral_action.triggered.connect(lambda: self.gui.change_background('neutral'))
        change_background_menu.addAction(background_neutral_action)

        background_black_action = QAction(self.gui.options_button)
        background_black_action.setText('&Black')
        background_black_action.triggered.connect(lambda: self.gui.change_background('black'))
        change_background_menu.addAction(background_black_action)

        self.pause_punctuation_action = QAction(self.gui.options_button)
        self.pause_punctuation_action.setIcon(self.gui.icons['punctuation_off'])
        self.pause_punctuation_action.setText('&Pause for Punctuation')
        self.pause_punctuation_action.triggered.connect(self.gui.pause_for_punctuation)
        self.pause_punctuation_action.setCheckable(True)
        self.addAction(self.pause_punctuation_action)

        self.group_words_action = QAction(self.gui.options_button)
        self.group_words_action.setIcon(self.gui.icons['combine_off'])
        self.group_words_action.setText('&Combine Small Words')
        self.group_words_action.triggered.connect(self.gui.combine_words)
        self.group_words_action.setCheckable(True)
        self.addAction(self.group_words_action)

        self.addSeparator()

        help_action = self.addAction('Help')
        help_action.triggered.connect(self.gui.show_help)
