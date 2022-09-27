import workers.graph
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import database.settings, database.domains
import logging

logger = logging.getLogger(__name__)


class top_view(QWidget):
    def __init__(self):
        super().__init__()

        # set layout of widget
        self.setLayout(QVBoxLayout())

        # obtain current settings
        settings = database.settings.current

        # obtain current domains
        domains = database.domains.current

        top_view = workers.graph.top_view(
            domains, settings.diameter, settings.theta_c, settings.theta_s
        )
        top_view.compute()
        logger.debug(top_view)

        plotted_window: pg.GraphicsLayoutWidget = (
            pg.GraphicsLayoutWidget()
        )  # create main plotting window
        plotted_window.setBackground("w")  # make the background white

        main_plot = plotted_window.addPlot()

        main_plot.plot(
            top_view.u_coords,
            top_view.v_coords,
            symbol="o",
            symbolSize=top_view.diameter,
            pxMode=False,
        )

        # increase the view box padding, since...
        # our symbols are VERY large circles and pyqtgraph calculates padding from the actual points, so the circles get cut off
        plotted_view_box = main_plot.getViewBox()
        plotted_view_box.setDefaultPadding(padding=0.18)

        # prevent user from interacting with the graph
        plotted_view_box.setAspectLocked(lock=True, ratio=1)

        # add the plot widget to the layout
        self.layout().addWidget(plotted_window)