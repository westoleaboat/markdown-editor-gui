# PyQt GUI application 
# markdown_editor.py : A simple text editor which display markdown text

import sys                              # pass QApplication an actual list of script arguments
from PyQt5 import QtWidgets as qtw      #
from PyQt5 import QtGui as qtg          # main Qt modules.
from PyQt5 import QtCore as qtc         #




class SettingsDialog(qtw.QDialog):
    """Dialog for setting the settings"""

    def __init__(self, settings, parent=None):
        super().__init__(parent, modal=True)
        self.setLayout(qtw.QFormLayout())
        self.settings = settings
        self.layout().addRow(
            qtw.QLabel('<h1>Application Settings</h1>'),
        )
        self.show_warnings_cb = qtw.QCheckBox(
            #checked=settings.get('show_warnings')
            checked=settings.value('show_warnings', type=bool)
        )
        self.layout().addRow("Show Warnings", self.show_warnings_cb)

        self.accept_btn = qtw.QPushButton('Ok', clicked=self.accept)
        self.cancel_btn = qtw.QPushButton('Cancel', clicked=self.reject)
        self.layout().addRow(self.accept_btn, self.cancel_btn)

    def accept(self):
        #self.settings['show_warnings'] = self.show_warnings_cb.isChecked()
        self.settings.setValue(
            'show_warnings',
            self.show_warnings_cb.isChecked()
        )
        print(self.settings.value('show_warnings'))
        super().accept()

class MainWindow(qtw.QMainWindow):

    settings = qtc.QSettings('PyQtEditor', 'markdown editor')

    def __init__(self):
        """
        MainWindow constructor. Subclass of QMainWindow

        This widget will be our main window.
        We'll define all the UI components in here.

        Constructor ends with a call to self.show(), 
        so our MainWindow will take care of showing itself.
        """
        super().__init__()
        # Main UI code goes here


        ######################
        # The central widget #
        ######################
        self.textedit = qtw.QTextEdit() # for more complex app can use Qwidget obj
        self.setCentralWidget(self.textedit)
        
        # Set the size of the main window
        self.setGeometry(100, 100, 800, 600)  # Position (100, 100) with a size of 800x600
        # Or use resize if you don't care about the position
        # self.resize(800, 600)
        # self.setMinimumSize(400, 300)
        # self.setMaximumSize(1200, 800)

        self.setWindowTitle('Markdown Editor')
        #################
        # The Statusbar #
        #################

        self.statusBar().showMessage('Welcome to Markdown Editor')

        # add widgets to statusbar
        charcount_label = qtw.QLabel("chars: 0")
        self.textedit.textChanged.connect(
            lambda: charcount_label.setText(
                "chars: " +
                str(len(self.textedit.toPlainText()))
                )
            )
        self.statusBar().addPermanentWidget(charcount_label)

        ###############
        # The menubar #
        ###############
        # On macOS, the native menu system has a few peculiarities that you need to be aware of.
        # More information about Qt menus on macOS can be found at 
        # https://doc.qt.io/qt-5/macos-issues.html#menu-bar.
        
        menubar = self.menuBar()

        # add submenus to a menu
        # some platforms will not display empty submenus.
        file_menu = menubar.addMenu('File')
        edit_menu = menubar.addMenu('Edit')
        help_menu = menubar.addMenu('Help')

        # add actions.
        # Actions are simply objects of the QAction class that 
        # represent things our program can do. To be useful, a
        # QAction object needs at least a name and a callback; 
        # they can optionally define a keyboard shortcut and 
        # icon for the action.
        open_action = file_menu.addAction('Open')
        save_action = file_menu.addAction('Save')
        md_action = file_menu.addAction('Markdown')

        # add separator
        file_menu.addSeparator()

        # QAction objects have a triggered signal that must be connected to a callable or slot for
        # the action to have any effect. This is handled automatically when we use the addAction()
        # method of creating actions, but it must be done manually when creating QAction objects
        # explicitly.

        # add an action with a callback
        quit_action = file_menu.addAction('Quit', self.close)

        # connect to a Qt Slot
        edit_menu.addAction('Undo', self.textedit.undo)

        # create a QAction manually
        # It's important to pass in a parent widget when creating a QAction object explicitly. 
        # Failing to do so will result in the item not showing up,
        redo_action = qtw.QAction('Redo', self)
        redo_action.triggered.connect(self.textedit.redo)
        edit_menu.addAction(redo_action)

        ############################
        # The Toolbar and QActions #
        ############################

        toolbar = self.addToolBar('File')

        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setAllowedAreas( # restrict the sides of the window to which the bar can be docked
            qtc.Qt.TopToolBarArea |
            qtc.Qt.BottomToolBarArea
        )

        self.markdown_enabled = False   # Flag to track markdown state
        self.raw_text = ""              # store raw markdown text

        # Add with icons
        open_icon = self.style().standardIcon(qtw.QStyle.SP_DirOpenIcon) # built-in style
        save_icon = self.style().standardIcon(qtw.QStyle.SP_DialogSaveButton)
        md_icon = self.style().standardIcon(qtw.QStyle.SP_FileIcon)

        open_action.setIcon(open_icon)
        save_action.setIcon(save_icon)
        md_action.setIcon(md_icon)

        toolbar.addAction(open_action)
        toolbar.addAction(save_action)

        toolbar.addAction(
            md_icon,
            'Toggle Markdown',
            lambda: self.showMarkdown()
        )

        ################
        # Dock Widgets #
        ################

        dock = qtw.QDockWidget("Replace")
        self.addDockWidget(qtc.Qt.LeftDockWidgetArea, dock)

        # make it not closable
        dock.setFeatures(
            qtw.QDockWidget.DockWidgetMovable |
            qtw.QDockWidget.DockWidgetFloatable
        )

        replace_widget = qtw.QWidget()
        replace_widget.setLayout(qtw.QVBoxLayout())
        dock.setWidget(replace_widget)

        self.search_text_inp = qtw.QLineEdit(placeholderText='search')
        self.replace_text_inp = qtw.QLineEdit(placeholderText='replace')
        search_and_replace_btn = qtw.QPushButton(
            "Search and Replace",
            clicked=self.search_and_replace
            )
        replace_widget.layout().addWidget(self.search_text_inp)
        replace_widget.layout().addWidget(self.replace_text_inp)
        replace_widget.layout().addWidget(search_and_replace_btn)
        replace_widget.layout().addStretch()

        ############################
        # Messageboxes and Dialogs #
        ############################

        # QMessageBox
        help_menu.addAction('About', self.showAboutDialog)


        if self.settings.value('show_warnings', False, type=bool):
            response = qtw.QMessageBox.question(
                self,
                'My Text Editor',
                'This is beta software, do you want to continue?',
                qtw.QMessageBox.Yes | qtw.QMessageBox.Abort
            )
            if response == qtw.QMessageBox.Abort:
                self.close()
                sys.exit()

            # custom message box

            splash_screen = qtw.QMessageBox()
            splash_screen.setWindowTitle('My Text Editor')
            splash_screen.setText('BETA SOFTWARE WARNING!')
            splash_screen.setInformativeText(
                'This is very, very beta, '
                'are you really sure you want to use it?'
            )
            splash_screen.setDetailedText(
                'This editor was written for pedagogical '
                'purposes, and probably is not fit for real work.'
            )
            splash_screen.setWindowModality(qtc.Qt.WindowModal)
            splash_screen.addButton(qtw.QMessageBox.Yes)
            splash_screen.addButton(qtw.QMessageBox.Abort)
            response = splash_screen.exec_()
            if response == qtw.QMessageBox.Abort:
                self.close()
                sys.exit()

        # QFileDialog
        open_action.triggered.connect(self.openFile)
        save_action.triggered.connect(self.saveFile)
        md_action.triggered.connect(self.showMarkdown)

        # Custom dialog
        edit_menu.addAction('Settings…', self.show_settings)

        # End main UI code
        self.show()

    def search_and_replace(self):
        s_text = self.search_text_inp.text()
        r_text = self.replace_text_inp.text()

        if s_text:
            self.textedit.setText(
                self.textedit.toPlainText().replace(s_text, r_text)
                )
    
    def showAboutDialog(self):
        qtw.QMessageBox.about(
            self,
            "About markdown_editor.py",
            "This is a text editor written in PyQt5.\nUse to edit Markdown text files."
        )

    def openFile(self):
        filename, _ = qtw.QFileDialog.getOpenFileName(
            self,
            "Select a text file to open…",
            qtc.QDir.homePath(),
            'Text Files (*.txt) ;;Python Files (*.py) ;;All Files (*)',
            'Python Files (*.py)',
            qtw.QFileDialog.DontUseNativeDialog |
            qtw.QFileDialog.DontResolveSymlinks
        )
        if filename:
            try:
                with open(filename, 'r') as fh:
                    self.textedit.setText(fh.read())
            except Exception as e:
                qtw.QMessageBox.critical(self, f"Could not load file: {e}")

    def saveFile(self):
        filename, _ = qtw.QFileDialog.getSaveFileName(
            self,
            "Select the file to save to…",
            qtc.QDir.homePath(),
            'Text Files (*.txt) ;;Python Files (*.py) ;;All Files (*)'
        )
        if filename:
            try:
                with open(filename, 'w') as fh:
                    fh.write(self.textedit.toPlainText())
            except Exception as e:
                qtw.QMessageBox.critical(self, f"Could not load file: {e}")
    
    def showMarkdown(self):

        if self.markdown_enabled:
            # Switch to raw text (markdown off)

            self.textedit.setReadOnly(False)
            self.textedit.setPlainText(self.raw_text)
            self.statusBar().showMessage('Markdown Off')
        else:
            self.textedit.setReadOnly(True)
            # Store the raw markdown text and switch to markdown view (markdown on)
            self.raw_text = self.textedit.toPlainText()  # Save the raw text before converting
            self.textedit.setMarkdown(self.raw_text)


            self.statusBar().showMessage('Markdown On')

        # Toggle the state
        self.markdown_enabled = not self.markdown_enabled

    def show_settings(self):

        settings_dialog = SettingsDialog(self.settings, self)
        settings_dialog.exec()

# Main code execution
if __name__ == '__main__':
    '''
    It's best practice to create the QApplication object at the 
    global scope (outside of any function or class). 
    This ensures that all Qt objects get properly closed 
    and cleaned up when the application quits.

    We pass sys.argv into QApplication(); Qt has several default
    command-line arguments that can be used for debugging or to alter styles and themes.
    These are processed by the QApplication constructor if you pass in sys.argv.

    We're calling app.exec() inside a call to sys.exit; this is a small touch
    that causes the exit code of app.exec() to be passed to sys.exit(), so we pass
    appropriate exit codes to the OS, if the underlying Qt instance crashes for some reason.
    '''
    # create QApplication object
    app = qtw.QApplication(sys.argv)

    # it's required to save a reference to MainWindow.
    # if it goes out of scope, it will be destroyed.

    # make MainWindow object
    mw = MainWindow()
    # call QApplication.exec()
    sys.exit(app.exec())