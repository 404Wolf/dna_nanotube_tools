import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QMenuBar,
    QWidget,
    QTabWidget, QHBoxLayout, QSplitter,
)

import settings

logger = logging.getLogger(__name__)


class Window(QMainWindow):
    """
    The nanotube constructor main window.

    Attributes:
        runner (Runner): NATuG's runner.
        status_bar (QStatusBar): The status bar.
        menu_bar (QMenuBar): The menu bar.
        toolbar (QToolBar): The toolbar.
        top_view (QWidget): Top view widget.
        side_view (QWidget): Side view widget.
    """

    def __init__(self, runner: "runner.Runner"):
        self.runner = runner

        # this is an inherited class of QMainWindow,
        # so we must initialize the strands qt widget
        super().__init__()

    def setup(self):
        # create plot panels
        self._plots()

        # utilize inherited methods to set up the refs window
        self.setWindowTitle(settings.name)

        # add all widgets
        self._config()

        # initialize status bar
        self._status_bar()

        # initialize menu bar
        self._menu_bar()

        # initialize toolbar
        self._toolbar()

    def _toolbar(self):
        """Setup toolbar."""

        # import the needed panel
        from ui.toolbar import Toolbar

        self.toolbar = Toolbar(self, self.runner)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

    def _config(self):
        """Setup config panel."""

        # import the needed panel
        from ui.config import Dockable

        # initialize the config panel
        self.config = Dockable(
            self,
            self.runner,
        )

        # only allow config to dock left/right
        self.config.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

        # trigger a resize event when the floatingness of the config panel changes
        self.config.topLevelChanged.connect(self.resizeEvent)

        # trigger a resize event on tab change
        self.config.panel.tab_area.currentChanged.connect(self.resizeEvent)

        # dock the new dockable config widget
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.config)

    def _plots(self):
        """
        Setup the central area of the main window.

        The central area is a tab widget that contains the major plots of NATuG: the
        side view and the top view plot. This method also initializes the plots.
        """
        from ui.panels.side_view import SideViewPanel
        from ui.panels.top_view.panel import TopViewPanel

        central_widget = QWidget()
        central_widget.setLayout(QHBoxLayout())
        plot_container = QSplitter()
        plot_container.setHandleWidth(5)
        central_widget.layout().addWidget(plot_container)

        self.top_view = TopViewPanel(self, self.runner)
        self.side_view = SideViewPanel(self, self.runner)

        plot_container.addWidget(self.top_view)
        plot_container.addWidget(self.side_view)
        plot_container.setSizes([250, 520])

        self.setCentralWidget(central_widget)

    def _status_bar(self):
        """Setup status bar."""
        status_bar = self.status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)
        self.statusBar().setStyleSheet("background-color: rgb(210, 210, 210)")
        logger.info("Created status bar.")

    def _menu_bar(self):
        """Setup menu bar."""
        from .menubar import Menubar

        self.menu_bar = Menubar(self, self.runner)
        self.setMenuBar(self.menu_bar)

        logger.info("Created menu bar.")

    def resizeEvent(self, event):
        """Dynamically resize panels."""
        # Resize the config based on whether it is floating (and thus it can be much
        # larger) or if it is docked (and thus it must be smaller).
        if self.config.isFloating():
            # Make the tab titles go on the top of the plot if there is enough
            # horizontal space
            self.config.tab_area.setTabPosition(QTabWidget.TabPosition.North)
            self.config.setMaximumWidth(400)
        else:
            # When the config panel is docked we want it to be as small as possible.
            # So, first we set the tabs to be on the right side (since it takes up
            # less horizontal space) and then we set the width of the config panel
            # based on the width that the currently visible panel requires.
            self.config.tab_area.setTabPosition(QTabWidget.TabPosition.East)
            if self.config.panel.sequencing.isVisible():
                self.config.setFixedWidth(255)
            elif self.config.panel.domains.isVisible():
                self.config.setFixedWidth(450)
            elif self.config.panel.nucleic_acid.isVisible():
                self.config.setFixedWidth(220)
