# Code by LegoStormtroopr
#
# License:
# This [trivial fingertab gist](https://gist.github.com/LegoStormtroopr/5075267) is released
# as Public Domain, but boy would it beswell if you could credit me, or tweet me
# [@LegoStormtoopr](http://www.twitter.com/legostormtroopr) to say thanks!

from qtutils.qt import QtCore, QtGui, QtWidgets


class FingerTabBarWidget(QtWidgets.QTabBar):
    def __init__(self, parent=None, *args, **kwargs):
        self.tabSize = QtCore.QSize(kwargs.pop('width', 100), kwargs.pop('height', 25))
        QtWidgets.QTabBar.__init__(self, parent, *args, **kwargs)

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        option = QtWidgets.QStyleOptionTab()

        for index in range(self.count()):
            self.initStyleOption(option, index)
            tabRect = self.tabRect(index)
            tabRect.moveLeft(10)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabShape, option)
            painter.drawText(tabRect, QtCore.Qt.AlignVCenter |
                             QtCore.Qt.TextDontClip,
                             self.tabText(index))
        painter.end()

    def tabSizeHint(self, index):
        return self.tabSize

# Shamelessly stolen from this thread:
#   http://www.riverbankcomputing.com/pipermail/pyqt/2005-December/011724.html
class FingerTabWidget(QtWidgets.QTabWidget):
    """A QTabWidget equivalent which uses our FingerTabBarWidget"""

    def __init__(self, parent, *args):
        QtWidgets.QTabWidget.__init__(self, parent, *args)
        self.setTabBar(FingerTabBarWidget(self))
