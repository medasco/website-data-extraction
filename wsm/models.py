
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os.path as p


class Node(QObject):
    """ Node Class """
    def __init__(self, name, parent=None, checkState=Qt.Unchecked):
        super(Node, self).__init__()
        # Protected Members
        self._name = name
        self._data = None
        self._children = []
        self._parent = parent
        self._checked = checkState

        if parent is not None:
            # Adds self as a child
            parent.add_child(self)
            # else: (root)

    # Setters
    def set_name(self, name):
        """ Method to set name of the Node """
        self._name = name

    def set_parent(self, parent):
        """ Method to set the parent Node """
        self._parent = parent
        parent.add_child(self)

    def set_checked(self, state):
        self._checked = state

        for c in self._children:
            c.set_checked(state)

    def set_data(self, data):
        self._data = data

    def add_child(self, child):
        """ Method to add child into the list """
        self._children.append(child)

    def remove_child(self, position):
        if position < 0 or position > len(self._children):
            return False

        child = self._children.pop(position)
        child._parent = None
        # del self._children[position]
        return True

    # Getters
    def name(self):
        """ Returns the name of the Node """
        return self._name

    def data(self, column):
        try:
            return self._data[column]
        except IndexError:
            return None

    def get_data(self):
        return self._data

    def child(self, row):
        """ Method that returns the child in its specified row """
        return self._children[row]

    def children(self):
        """ Method that returns the children list """
        return self._children

    def child_count(self):
        """ Method that returns the total count of children in a Node """
        return len(self._children)

    def parent(self):
        """ Method that returns the parent Node """
        return self._parent

    def row(self):
        """ Method that returns the index of Node relative to its parent """
        if self._parent is not None:
            return self._parent._children.index(self)
        return 0

    def checked(self):
        """ Method that return checked state of Node """
        return self._checked


class ClubNode(Node):
    def __init__(self, clubName, parent=None):
        super(ClubNode, self).__init__(clubName, parent)
        # Node data is emptied except the country name
        self._data = [clubName]

    def type_info(self):
        return "CLUB"


class CountryNode(Node):
    def __init__(self, countryName, parent=None):
        super(CountryNode, self).__init__(countryName, parent)
        # Node data is emptied except the country name
        self._data = [countryName]

    def type_info(self):
        return "COUNTRY"


class IcaoNode(Node):
    def __init__(self, icaoName, countryName, parent=None):
        super(IcaoNode, self).__init__(icaoName, parent)
        self._name = icaoName
        self._data = [icaoName, countryName]

    def type_info(self):
        return "ICAO"


class ChartNode(Node):
    def __init__(self, icaoName, parent=None, data=None):
        super(ChartNode, self).__init__(icaoName, parent, data)
        self._data = data

    def type_info(self):
        return "CHART"


class ChartTreeModel(QAbstractItemModel):
    checkChanged = pyqtSignal()

    def __init__(self, root: Node, parent=None):
        """ Inputs: Node, QModelIndex
        """
        super(ChartTreeModel, self).__init__(parent)
        self._rootNode = root

    def getRootNode(self):
        return self._rootNode

    def getNode(self, index):
        """ Custom
            Inputs: QModelIndex
        """
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node

        return self._rootNode

    def getChartNodes(self):
        charts = []
        for clubNode in self._rootNode.children():
            for countryNode in clubNode.children():
                for icaoNode in countryNode.children():
                    for chartNode in icaoNode.children():
                        if chartNode.checked() == Qt.Checked:
                            charts.append(chartNode)
        return charts

    def parent(self, index=None):
        node = self.getNode(index)
        parent_node = node.parent()

        if parent_node != self._rootNode:
            return self.createIndex(parent_node.row(), 0, parent_node)

        return QModelIndex()

    def index(self, row, column, parent=None, *args, **kwargs):
        """ Inputs: int, int, QModelIndex
            Output: QModelIndex
        """
        parent_node = self.getNode(parent)

        child_item = parent_node.child(row)

        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()

    def rowCount(self, parent=None, *args, **kwargs):
        """ Inputs: QModelIndex
            Output: int
        """
        if not parent.isValid():
            parent_node = self._rootNode
        else:
            parent_node = parent.internalPointer()

        return parent_node.child_count()

    def columnCount(self, parent=None, *args, **kwargs):
        """ Inputs: QModelIndex
            Output: int
        """
        return 1

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable

    def data(self, index, role=None):
        """ Inputs: QModelIndex, int
            Output:
        """
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return node.name()

        if role == Qt.CheckStateRole:
            return node.checked()

    def headerData(self, section, orientation, role=None):
        if role == Qt.DisplayRole:
            if section == 0:
                return "Charts"

    def setData(self, index, value, role=Qt.CheckStateRole):
        if role == Qt.EditRole:
            return False

        if index.isValid() and role == Qt.CheckStateRole:
            node = index.internalPointer()

            # Toggle check mark
            # node.set_checked(not node.checked())
            node.set_checked(value)
            # Emit check state change signal
            self.checkChanged.emit()

            self.dataChanged.emit(index, index)
            self.emitDataChangedForChildren(index)
            return True

        return False

    def emitDataChangedForChildren(self, index):
        count = self.rowCount(index)
        if count:
            self.dataChanged.emit(index.child(0, 0), index.child(count - 1, 0))
            for child in range(count):
                self.emitDataChangedForChildren(index.child(child, 0))


class LeafFilterProxyModel(QSortFilterProxyModel):
    """ Class to override the following behaviour:
            If a parent item doesn't match the filter,
            none of its children will be shown.

        This Model matches items which are descendants
        or ascendants of matching items.
    """

    def filterAcceptsRow(self, row_num, source_parent):
        """ Overriding the parent function """

        # Check if the current row matches
        if self.filter_accepts_row_itself(row_num, source_parent):
            return True

        # Traverse up all the way to root and check if any of them match
        if self.filter_accepts_any_parent(source_parent):
            return True

        # Finally, check if any of the children match
        return self.has_accepted_children(row_num, source_parent)

    def filter_accepts_row_itself(self, row_num, parent):
        return super(LeafFilterProxyModel, self).filterAcceptsRow(row_num, parent)

    def filter_accepts_any_parent(self, parent):
        """ Traverse to the root node and check if any of the
            ancestors match the filter
        """
        while parent.isValid():
            if self.filter_accepts_row_itself(parent.row(), parent.parent()):
                return True
            parent = parent.parent()
        return False

    def has_accepted_children(self, row_num, parent):
        """ Starting from the current node as root, traverse all
            the descendants and test if any of the children match
        """
        model = self.sourceModel()
        source_index = model.index(row_num, 0, parent)

        children_count = model.rowCount(source_index)
        for i in range(children_count):
            if self.filterAcceptsRow(i, source_index):
                return True
        return False


class ChartTableModel(QAbstractTableModel):

    def __init__(self, parent=None):
        super(ChartTableModel, self).__init__(parent)
        self._icaoNodes = None
        self._headers = None

    def setHeaders(self, headers: []):
        self._headers = headers

    def getHeader(self, pos):
        return self._headers[pos]

    def getChartList(self):
        return self._icaoNodes

    def setContents(self, contents: [ChartNode]):
        self._icaoNodes = None
        self._icaoNodes = contents
        self.layoutChanged.emit()

    def setFileName(self, row, new_name):
        # Remove the '.pdf'
        fn = new_name
        if new_name.endswith('.pdf'):
            fn = new_name.split('.pdf')[0]

        if new_name.endswith('.PDF'):
            fn = new_name.split('.PDF')[0]

        self._icaoNodes[row].get_data()[3] = fn

    def setProgress(self, status, row):
        self._icaoNodes[row].get_data()[1] = status
        self.layoutChanged.emit()

    def flags(self, index):
        if index.column() == 3:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._icaoNodes)

    def columnCount(self, *args, **kwargs):
        return len(self._headers)

    def data(self, index, role=None):

        row = index.row()
        column = index.column()

        if role == Qt.DisplayRole or role == Qt.EditRole:

            value = self._icaoNodes[row].data(column)
            if column == 1:
                if value == 100:
                    return 'Done'

            return value

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
            # if column == 1:
            #     return Qt.AlignLeft
            # else:
            #     return Qt.AlignCenter

        # TODO: This is not working
        # if role == Qt.FontRole:
        #     if column == 0:
        #         return QFont.Bold
        #     else:
        #         return QFont.StyleItalic

    def insertRows(self, position, rows, parent=None, *args, **kwargs):
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)

        self.endInsertRows()

    def removeRows(self, position, rows, parent=None, *args, **kwargs):
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)

        for i in range(rows):
            value = self._icaoNodes[position]
            self._icaoNodes.remove(value)

        self.endRemoveRows()

    def clearRows(self):
        self.removeRows(0, self.rowCount())

    def setData(self, index, value, role=None):
        row = index.row()
        column = index.column()

        if role == Qt.EditRole:
            if column == 3:
                self.setFileName(row, value)
                return True

        return False


class ProgressDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        progressBar = QStyleOptionProgressBarV2()
        progressBar.state = QStyle.State_Enabled
        progressBar.direction = QApplication.layoutDirection()
        progressBar.rect = QRect(option.rect.left(), option.rect.top()+4,
                                 option.rect.width(), option.rect.height()-8)  # option.rect
        progressBar.fontMetrics = QApplication.fontMetrics()
        progressBar.minimum = 0
        progressBar.maximum = 100
        progressBar.textAlignment = Qt.AlignLeft
        progressBar.textVisible = False

        prog = index.data()
        if prog != 'Done':
            #IbarretaI: TODO
            if int(prog) > 100:
                progressBar.setMinimum = 0
                progressBar.maximum = 0
            ###
            else:
                progressBar.progress = prog
        else:
            progressBar.progress = 100

        QApplication.style().drawControl(QStyle.CE_ProgressBar, progressBar, painter)

        return super(ProgressDelegate, self).paint(painter, option, index)


class TableSortFilterProxyModel(QSortFilterProxyModel):

    def headerData(self, section, orientation, role=None):
        if role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return section + 1
            if orientation == Qt.Horizontal:
                return self.sourceModel().getHeader(section)
