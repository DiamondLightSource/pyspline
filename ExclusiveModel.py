
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class ExclusiveModel(QStandardItemModel):
    def __init__(self, parent=None):
        QStandardItemModel.__init__(self, parent)

    def setData(self, index, value, role=Qt.EditRole):
        # Call base class method
        return_value = QStandardItemModel.setData(self, index,value, role)
        # Check if all other items must be unchecked
        if role == Qt.CheckStateRole:
            changed_item = self.itemFromIndex(index)
            if changed_item.checkState() == Qt.Checked:
                for row in range(self.rowCount()):
                    item = self.item(row, 0)
                    if item.text() != changed_item.text():
                        new_value = QVariant(Qt.Unchecked)
                        new_index = self.indexFromItem(item)
                        QStandardItemModel.setData(self,new_index, new_value, role)
            if changed_item.checkState() == Qt.Unchecked:
                for row in range(self.rowCount()):
                    item = self.item(row, 0)
                    if item.text() == changed_item.text():
                        new_value = QVariant(Qt.Checked)
                        new_index = self.indexFromItem(item)
                        QStandardItemModel.setData(self,new_index, new_value, role)


        return return_value
