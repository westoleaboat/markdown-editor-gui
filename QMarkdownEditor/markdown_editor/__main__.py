import sys
from PyQt5.QtWidgets import QApplication
from .mainwindow import MainWindow

def main():
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
    app = QApplication(sys.argv)

    # it's required to save a reference to MainWindow.
    # if it goes out of scope, it will be destroyed.

    # make MainWindow object
    mw = MainWindow()
    # call QApplication.exec()
    sys.exit(app.exec())

# Main code execution
if __name__ == '__main__':
    main()