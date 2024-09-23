import numpy as np
from qtpy import QtWidgets, QtCore
from arkitekt_next.qt import devqt, MagicBar
from mikro_next.api.schema import Image, from_array_like
from koil.qt import QtFuture, QtGenerator
import sys


class Dialog(QtWidgets.QWidget):
    def __init__(self, future: QtFuture[bool], parent=None):
        super().__init__(parent)
        self.future = future
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setFixedSize(200, 100)

        self.accept_button = QtWidgets.QPushButton("Accept")
        self.accept_button.clicked.connect(self.on_accept)

        self.reject_button = QtWidgets.QPushButton("Reject")
        self.reject_button.clicked.connect(self.on_reject)


        self.future.cancelled.connect(self.close)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.accept_button)
        layout.addWidget(self.reject_button)
        self.setLayout(layout)

    def on_accept(self):
        self.future.resolve(True)
        self.close()

    def on_reject(self):
        self.future.resolve(False)
        self.close()




class GeneratorDialog(QtWidgets.QWidget):
    def __init__(self, generator: QtGenerator[str], parent=None):
        super().__init__(parent)
        self.generator = generator
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setFixedSize(200, 100)

        self.next_button = QtWidgets.QPushButton("Next")
        self.next_button.clicked.connect(self.next)

        self.reject_button = QtWidgets.QPushButton("Done")
        self.reject_button.clicked.connect(self.close)
        self.generator.cancelled.connect(self.close)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.next_button)
        layout.addWidget(self.reject_button)
        self.setLayout(layout)
        self.i = 0

    def next(self):
        self.generator.next(f"Another {self.i}")
        self.i += 1

    def close(self):
        self.generator.stop()
        super().close()



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the app
        # Every Arkitekt Next app needs to be created with a unique identifier
        # You can choose between publiqt and devqt
        # PublicQt allows multiple users to sign in with this app
        # DevQt is for development purposes and only allows one user to sign in
        self.app = devqt("my_app_name") # or publicqt


        # Create the magic bar
        # The magic bar is a widget that can be used to interact with the app 
        # (e.g login or sign out, as well as start the provisioning loop)
        self.magic_bar = MagicBar(self.app)




        self.setWindowTitle("My App")
        self.setCentralWidget(self.magic_bar)

        self.active_dialogs = {}


        # Function Registration
        # We illustrate different strategies here
        # the description is in the function definitions
        self.app.register(self.upload_image)
        self.app.register_with_qt_generator(self.yield_anothers)
        self.app.register_with_qt_future(self.require_user)
        self.app.register_in_qt_loop(self.ask_blocking)


    def upload_image(self) -> Image:


        # This function will be called in a seperate thread
        # to avoid blocking the main thread, this is the
        # default behavior for functions registered with the app
        # and allows for efficient upload of data
        
        return from_array_like(np.random.rand(100, 100), name="random_image")
    

    def ask_blocking(self, message: str = "Do you want to block me forever?") -> bool:

        # This function will be called in the main thread
        # and will block the main thread and therefore the ui until the user
        # has made a choice
        # This strategy is only recommended for short operations
        # or when the user is expected to make a choice

        button = QtWidgets.QMessageBox.question(
            self,
            "Blocking Dialog",
            message,
        )

        if button == QtWidgets.QMessageBox.StandardButton.Yes:
            return True
        else:
            return False

        

    def require_user(self, future: QtFuture[bool], message: str = "Do you accept?"):

        # This function will be called in the main thread
        # and will not block the main thread, but will
        # wait for the user to make a choice
        # before resolving the future

        # Futures can be resolved from any thread


        # In order to inspect the correct return type 
        # please specify th return type in the QtFuture Generic
        # e.g. QtFuture[bool]

    
        dialog = Dialog(future)
        dialog.setWindowTitle(message)
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        dialog.setFixedSize(200, 100)


        dialog.show()

        self.active_dialogs[future.id] = dialog
        print("Dialog shown")
       
    

    def yield_anothers(self, generator: QtGenerator[str]):

        # This function will be called in the main thread
        # and will not block the main thread, but will
        # wait for the user to make choices that are then
        # yielded to the generator

        # Generators can yield from any thread
        # In order to inspect the correct return type 
        # please specify th return type in the QtGenerator Generic
        # e.g. QtGenerator[bool]


        dialog = GeneratorDialog(generator)
        dialog.show()

        self.active_dialogs[generator.id] = dialog



if __name__  == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
