# PyQt GUI application 
# markdown_editor.py : A simple text editor which display markdown text

import sys                              # pass QApplication an actual list of script arguments
from PyQt5 import QtWidgets as qtw      #
from PyQt5 import QtGui as qtg          # main Qt modules.
from PyQt5 import QtCore as qtc         #

import os


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

# creating VLine class
class VLine(qtw.QFrame):

    # a simple Vertical line
    def __init__(self):

        super(VLine, self).__init__()
        self.setFrameShape(self.VLine|self.Sunken)

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
        self.folder_path = "/home/wings/Files/criptoarica/recursos_md"
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

        #################
        # The Statusbar #
        #################

        self.statusBar().showMessage('Welcome to Markdown Editor')

        # add widgets to statusbar
        charcount_label = qtw.QLabel("chars: 0")
        # charcount_label.setStyleSheet("border :2px solid grey;")

        self.file_name_label = qtw.QLabel("no file open") # For status bar
        self.current_file = None
        self.is_dirty = False
        self.loading_file = False

        # Cuenta los caracteres en el archivo
        self.textedit.textChanged.connect(
            lambda: charcount_label.setText(
                "chars: " +
                str(len(self.textedit.toPlainText()))
                )
            )
        
        self.textedit.textChanged.connect(self.on_text_changed) # change title on trackiong dirty files

        self.update_window_title()
        

        self.toggle_md_btn = qtw.QPushButton(f"MarkDown Off", self, checkable=True, checked=False) # extra toggle markdown button (not used)
        self.toggle_md_btn.clicked.connect(self.showMarkdown)

        self.md_shortcut = qtw.QShortcut(qtg.QKeySequence("Ctrl+Tab"), self) # add shortcut directly instead of specific button because widget loses focus
        self.md_shortcut.activated.connect(self.showMarkdown)
        
        # self.statusBar().addPermanentWidget(self.toggle_md_btn) # since shortcut is added directly no need for extra toggle markdown button
        self.statusBar().addPermanentWidget(self.file_name_label)
        # adding VLine object
        self.statusBar().addPermanentWidget(VLine())
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

        new_action = file_menu.addAction('New')#, self.newFile())
        new_action.triggered.connect(self.newFile)

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
        new_icon = self.style().standardIcon(qtw.QStyle.SP_FileLinkIcon)

        open_action.setIcon(open_icon)
        save_action.setIcon(save_icon)
        md_action.setIcon(md_icon)
        new_action.setIcon(new_icon)

        toolbar.addAction(open_action)
        toolbar.addAction(save_action)

        toolbar.addAction(
            md_icon,
            'Toggle Markdown',
            lambda: self.showMarkdown(),
        )

        toolbar.addAction(new_action)

        ################
        # Dock Widgets #
        ################

        dock = qtw.QDockWidget("Dock")
        self.addDockWidget(qtc.Qt.LeftDockWidgetArea, dock)

        # make it not closable
        dock.setFeatures(
            qtw.QDockWidget.DockWidgetMovable |
            qtw.QDockWidget.DockWidgetFloatable
        )

        # Create container widget for everything
        container_widget = qtw.QWidget()
        container_layout = qtw.QVBoxLayout(container_widget)

        # Search / replace controls
        self.search_text_inp = qtw.QLineEdit(placeholderText='search')
        self.replace_text_inp = qtw.QLineEdit(placeholderText='replace')
        search_and_replace_btn = qtw.QPushButton(
            "Search and Replace",
            clicked=self.search_and_replace
            )

        # Search/replace group
        search_group = qtw.QGroupBox("Search / Replace")
        search_layout = qtw.QVBoxLayout()

        search_layout.addWidget(self.search_text_inp)
        search_layout.addWidget(self.replace_text_inp)
        search_layout.addWidget(search_and_replace_btn)

        search_group.setLayout(search_layout)


        self.file_list = qtw.QListWidget()
        self.file_list.itemDoubleClicked.connect(self.open_md_file_from_list)


        # File list group
        file_group = qtw.QGroupBox("Markdown Files")
        file_layout = qtw.QVBoxLayout()
        file_layout.addWidget(self.file_list)
        file_group.setLayout(file_layout)

        # Add to main container
        container_layout.addWidget(search_group)
        container_layout.addWidget(file_group)
        container_layout.addStretch()

        dock.setWidget(container_widget)
        # self.file_list.itemDoubleClicked.connect(self.open_md_file_from_list)

        self.load_md_files()
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

    
    #########################
    # Dock widget functions #
    #########################

    def load_md_files(self): # MD files list widget
        """Load all .md files from self.folder_path into the list."""
        self.file_list.clear()
        self.current_file_item = None  # reset reference when rebuilding list

        if not os.path.isdir(self.folder_path):
            return

        for file_name in sorted(os.listdir(self.folder_path)):
            full_path = os.path.join(self.folder_path, file_name)

            if os.path.isfile(full_path) and file_name.lower().endswith(".md"):
                item = qtw.QListWidgetItem(file_name)
                item.setData(qtc.Qt.UserRole, full_path)
                self.file_list.addItem(item)

        # Re-apply highlight if current file is in this folder/list
        self.update_current_file_highlight()

    def search_and_replace(self):
        s_text = self.search_text_inp.text()
        r_text = self.replace_text_inp.text()

        # Clear any previous highlights
        self.clear_highlights()

        if s_text and r_text:
            self.textedit.setText(
                self.textedit.toPlainText().replace(s_text, r_text)
                )

        elif s_text and not r_text:
            # Highlight found text
            cursor = self.textedit.textCursor()
            document = self.textedit.document()

            #Format for highlight
            highlight_format = qtg.QTextCharFormat()
            highlight_format.setBackground(qtg.QColor("yellow"))

            # Reset cursor to start
            cursor.setPosition(0)
            self.textedit.setTextCursor(cursor)

            while True:
                cursor = document.find(s_text, cursor)
                if cursor.isNull():
                    break
                # Apply highlight
                cursor.mergeCharFormat(highlight_format)

    #############################
    # END Dock widget functions #
    #############################
        
    def clear_highlights(self):
        cursor = self.textedit.textCursor()
        cursor.beginEditBlock()

        # Select all text
        cursor.select(qtg.QTextCursor.Document)

        # Clear format
        clear_format = qtg.QTextCharFormat()
        clear_format.setBackground(qtg.QColor("transparent"))

        cursor.mergeCharFormat(clear_format)
        cursor.endEditBlock()

    def showAboutDialog(self):
        qtw.QMessageBox.about(
            self,
            "About markdown_editor.py",
            "This is a text editor written in PyQt5.\nUse to edit Markdown text files."
        )

    def showNewFileDialog(self):
        # qtw.QMessageBox.newfile(
        if self.current_file != None:
            qtw.QMessageBox.information(
                    self,
                    "New File",
                    "The current file will be closed!"
            )
        
    def newFile(self):
        self.showNewFileDialog()

        self.loading_file = True
        self.current_file = None
        self.textedit.clear()
        self.loading_file = False

        self.file_name_label.setText("new file open")
        self.statusBar().showMessage(f"New file created!")

        self.is_dirty = False
        self.update_window_title()  

        # self.current_file_item = None
        self.update_current_file_highlight()

    def on_text_changed(self):
        """Mark document as dirty when text changes."""
        if getattr(self, "loading_file", False):
            return
        self.is_dirty = True
        self.update_window_title()

    def update_window_title(self):
        """Update window title to show current file and unsaved changes."""
        current_file = getattr(self, "current_file", None)
        is_dirty = getattr(self, "is_dirty", False)

        if current_file:
            file_name = os.path.basename(current_file)
        else:
            file_name = "Untitled"

        dirty_mark = " *" if is_dirty else ""
        self.setWindowTitle(f"{file_name}{dirty_mark} - Markdown Editor")

    def load_file_into_editor(self, filename):
        """Open a file and make it the current editing target."""
        if not filename:
            return

        self.showNewFileDialog()

        try:
            with open(filename, 'r', encoding='utf-8') as fh:
                self.markdown_enabled = False
                self.textedit.setPlainText(fh.read())

            # Single source of truth for currently open file
            self.current_file = os.path.abspath(filename)

            # Update UI
            file_name = os.path.basename(self.current_file)
            self.file_name_label.setText(file_name)
            self.statusBar().showMessage(f"Opened file: {self.current_file}")

            # Update persistent dock highlight
            self.update_current_file_highlight()
            self.is_dirty = False
            self.update_window_title()

        except Exception as e:
            qtw.QMessageBox.critical(self, "Error", f"Could not load file:\n{e}")

    def openFile(self):
        filename, _ = qtw.QFileDialog.getOpenFileName(
        self,
        "Select a text file to open…",
        qtc.QDir.homePath(),
        'Text Files (*.txt) ;;Python Files (*.py) ;;All Files (*) ;;Markdown Files (*.md)',
        'Markdown Files (*.md)',
        qtw.QFileDialog.DontUseNativeDialog |
        qtw.QFileDialog.DontResolveSymlinks
        )
        if filename:
            self.showNewFileDialog()
            try:
                full_path = os.path.abspath(filename)

                # Set state BEFORE loading text
                self.loading_file = True
                self.current_file = full_path
                self.markdown_enabled = False

                with open(full_path, 'r', encoding="utf-8") as fh:
                    self.textedit.setPlainText(fh.read())

                self.loading_file = False

                file_name = qtc.QFileInfo(full_path).fileName()
                self.file_name_label.setText(file_name)
                self.statusBar().showMessage(f"Open File {full_path}")

                self.highlight_current_file_in_list(file_name)

                # Clean state after opening
                self.is_dirty = False
                self.update_window_title()

                print(f'{filename}')

            except Exception as e:
                self.loading_file = False
                qtw.QMessageBox.critical(self, "Error", f"Could not load file: {e}")

    def update_current_file_highlight(self):
        """Persistently highlight the currently open file in the list."""
        self.current_file_item = None

        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            item_path = item.data(qtc.Qt.UserRole)

            # Reset all items to normal style
            font = item.font()
            font.setBold(False)
            item.setFont(font)
            item.setBackground(qtg.QBrush())  # default
            item.setForeground(qtg.QBrush())  # default

            # Highlight the currently open file
            if self.current_file and item_path == self.current_file:
                font.setBold(True)
                item.setFont(font)
                item.setBackground(qtg.QColor("#1f6f4a"))   # dark green
                item.setForeground(qtg.QColor("white"))
                self.current_file_item = item

    def open_md_file_from_list(self, item):
        file_path = item.data(qtc.Qt.UserRole)
        self.load_file_into_editor(file_path)

    def openFileDirect(self, filename):
        self.load_file_into_editor(filename)

    def saveFile(self):
        # If we already have a current file, prefill its path
        if self.current_file:
            default_path = self.current_file
        else:
            default_path = self.folder_path

        filename, _ = qtw.QFileDialog.getSaveFileName(
            self,
            "Select the file to save to…",
            default_path,
            'Markdown Files (*.md);;Text Files (*.txt);;Python Files (*.py);;All Files (*)',
            'Markdown Files (*.md)'
        )

        if filename:
            try:
                full_path = os.path.abspath(filename)

                with open(full_path, 'w', encoding="utf-8") as fh:
                    fh.write(self.textedit.toPlainText())

                self.current_file = full_path
                self.file_name_label.setText(os.path.basename(full_path))
                self.statusBar().showMessage(f"File saved as {full_path}")

                self.load_md_files()

                # Mark clean after save
                self.is_dirty = False
                self.update_window_title()

            except Exception as e:
                qtw.QMessageBox.critical(self, "Error", f"Could not save file: {e}")

    def showMarkdown(self):

        self.loading_file = True

        if self.markdown_enabled:
            # Switch to raw text (markdown off)
            self.textedit.setReadOnly(False)
            self.textedit.setPlainText(self.raw_text)
            self.statusBar().showMessage('Markdown Off')
            self.toggle_md_btn.setChecked(False)
            self.toggle_md_btn.setText("MarkDown Off")
        else:
            self.textedit.setReadOnly(True)
            # Store the raw markdown text and switch to markdown view (markdown on)
            self.raw_text = self.textedit.toPlainText()  # Save the raw text before converting
            self.textedit.setMarkdown(self.raw_text)
            self.toggle_md_btn.setText("MarkDown On")
            self.toggle_md_btn.setChecked(True)
            self.statusBar().showMessage('Markdown On')

        self.loading_file = False

        # Toggle the state
        self.markdown_enabled = not self.markdown_enabled
        
        self.update_window_title()
        
    def show_settings(self):

        settings_dialog = SettingsDialog(self.settings, self)
        settings_dialog.exec()

