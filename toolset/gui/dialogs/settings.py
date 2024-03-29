from PyQt5.QtWidgets import QDialog, QWidget, QTreeWidgetItem


class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        from toolset.uic.dialogs import settings
        self.ui = settings.Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.settingsTree.itemClicked.connect(self.pageChanged)

        self.pageDict = {
            "Installations": self.ui.installationsPage,
            "GIT Editor": self.ui.gitEditorPage,
            "Misc": self.ui.miscPage,
            "Module Designer": self.ui.moduleDesignerPage
        }

    def pageChanged(self, pageTreeItem: QTreeWidgetItem) -> None:
        newPage = self.pageDict[pageTreeItem.text(0)]
        self.ui.settingsStack.setCurrentWidget(newPage)

    def accept(self) -> None:
        super().accept()

        self.ui.miscWidget.save()
        self.ui.gitEditorWidget.save()
        self.ui.moduleDesignerWidget.save()
        self.ui.installationsWidget.save()
