# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui


class HomebrewTab(QtWidgets.QWidget):
    """
    Homebrew
    """
    def __init__(self, common):
        super(HomebrewTab, self).__init__()
        self.c = common

        self.c.log('HomebrewTab', '__init__')

        self.should_show = False

        # Widgets
        self.formulae_label = QtWidgets.QLabel("Updates are available for the following packages:")
        self.formulae_list_label = QtWidgets.QLabel()
        self.formulae_list_label.setStyleSheet(self.c.gui.css['HomebrewView package_names'])
        self.casks_label = QtWidgets.QLabel("Updates are available for the following apps:")
        self.casks_list_label = QtWidgets.QLabel()
        self.casks_list_label.setStyleSheet(self.c.gui.css['HomebrewView package_names'])
        instructions_label = QtWidgets.QLabel('Click "Install Updates" to open a Terminal and install updates using Homebrew.\nYou may have to type your macOS password if asked.')

        # Buttons
        install_updates_button = QtWidgets.QPushButton("Install Updates")
        install_updates_button.clicked.connect(self.clicked_install_updates_button)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(install_updates_button)
        buttons_layout.addStretch()

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.formulae_label)
        layout.addWidget(self.formulae_list_label)
        layout.addWidget(self.casks_label)
        layout.addWidget(self.casks_list_label)
        layout.addWidget(instructions_label)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        self.setLayout(layout)

    def homebrew_updates_available(self, outdated_formulae, outdated_casks):
        self.c.log('HomebrewTab', 'homebrew_updates_available', 'outdated_formulae={}, outdated_casks={}'.format(outdated_formulae, outdated_casks))
        self.should_show = True

        if len(outdated_formulae) == 0:
            self.formulae_label.hide()
            self.formulae_list_label.hide()
        else:
            self.formulae_label.show()
            self.formulae_list_label.show()
            self.formulae_list_label.setText('\n'.join(outdated_formulae))

        if len(outdated_casks) == 0:
            self.casks_label.hide()
            self.casks_list_label.hide()
        else:
            self.casks_label.show()
            self.casks_list_label.show()
            self.casks_list_label.setText('\n'.join(outdated_casks))

    def clicked_install_updates_button(self):
        self.c.log('HomebrewTab', 'clicked_install_updates_button')
        subprocess.run('osascript -e \'tell application "Terminal" to do script "brew cask upgrade && exit"\'', shell=True)
