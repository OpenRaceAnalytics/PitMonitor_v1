from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton

# Only needed for access to command line arguments
import sys 
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        button = QPushButton("Reboot")
        button.setCheckable(True)
        button.clicked.connect(self.the_button_was_clicked)

        # Set the central widget of the Window.
        self.setCentralWidget(button)

    def the_button_was_clicked(self):
        print("Clicked!")
        os.system("sudo reboot")
        self.close()


app = QApplication(sys.argv)

window = MainWindow()
window.showFullScreen()  # IMPORTANT!!!!! Windows are hidden by default.

# Start the event loop.
app.exec()


# Your application won't reach here until you exit and the event
# loop has stopped.
