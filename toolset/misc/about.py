from PyQt5.QtWidgets import QDialog, QWidget

from misc import about_ui


class About(QDialog):
    def __init__(self, parent: QWidget, version: str):
        super().__init__(parent)
        self.ui = about_ui.Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.closeButton.clicked.connect(self.close)

        self.ui.aboutLabel.setText(self.ui.aboutLabel.text().replace("X.X.X", version))
