import logging
from functools import partial

from PyQt6 import uic
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QSizePolicy,
)

import helpers
import refs
import settings
from structures.domains import Domains
from ui.panels.domains.table import Table
from ui.resources import fetch_icon

logger = logging.getLogger(__name__)


class Panel(QWidget):
    """Nucleic Acid Config Tab."""

    updated = pyqtSignal()

    def __init__(self, parent) -> None:
        super().__init__(parent)
        uic.loadUi("ui/panels/domains/panel.ui", self)

        # create domains editor table and append it to the bottom of the domains panel
        self.table = Table(self)
        self.layout().addWidget(self.table)

        # set initial values of domain table config widgets
        self.subunit_count.setValue(refs.domains.current.subunit.count)
        self.symmetry.setValue(refs.domains.current.symmetry)
        self.total_count.setValue(refs.domains.current.count)

        # run setup functions
        self._signals()
        self._prettify()

        # run an initial refresh
        self.table_refresh()
        self.settings_refresh()

        logger.info("Loaded domains tab of config panel.")

    def _signals(self):
        """Set up panel signals."""

        def update_total_domain_box():
            self.total_count.setValue(
                self.symmetry.value() * self.subunit_count.value()
            )

        self.symmetry.valueChanged.connect(update_total_domain_box)
        self.subunit_count.valueChanged.connect(update_total_domain_box)

        # when helix joint buttons are clicked refresh the table
        # so that the switch values (-1, 0, 1) get udpated
        self.table.helix_joint_updated.connect(self.table_refresh)

        # dump the initial domains
        self.table.dump_domains(refs.domains.current)

        # updated event linking
        self.update_table.clicked.connect(self.table_refresh)
        self.update_table.clicked.connect(self.settings_refresh)
        self.update_table.clicked.connect(self.updated.emit)

        self.table.cell_widget_updated.connect(self.table_refresh)
        self.table.cell_widget_updated.connect(self.settings_refresh)
        self.table.cell_widget_updated.connect(self.updated.emit)

    def _prettify(self):
        """Set up styles of panel."""
        # set reload table widget
        self.update_table.setIcon(fetch_icon("checkmark-outline"))

        # set scaling settings for config and table
        config_size_policy = QSizePolicy()
        config_size_policy.setVerticalPolicy(QSizePolicy.Policy.Fixed)
        config_size_policy.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        self.config.setSizePolicy(config_size_policy)

    def settings_refresh(self):
        # set M and target M boxes
        # https://github.com/404Wolf/NATuG3/issues/4
        current_domains = refs.domains.current
        M: int = sum(
            [domain.theta_interior_multiple for domain in current_domains.domains]
        )
        N: int = current_domains.count
        B: int = refs.nucleic_acid.current.B
        R: int = current_domains.symmetry
        target_M_over_R = (B * (N - 2)) / (2 * R)
        M_over_R = M / R
        self.M.setValue(M)

        # remove trailing zeros if target_M_over_R is an int
        if target_M_over_R == round(target_M_over_R):
            self.target_M_over_R.setDecimals(0)
        else:
            self.target_M_over_R.setDecimals(3)
        self.target_M_over_R.setValue(target_M_over_R)

        # remove trailing zeros if M_over_R is an int
        if M_over_R == round(M_over_R):
            self.M_over_R.setDecimals(0)
        else:
            self.M_over_R.setDecimals(3)
        self.M_over_R.setValue(M_over_R)

        # make M_over_R and target_M_over_R box green if it is the target
        if M_over_R == target_M_over_R:
            style = (
                f"QDoubleSpinBox{{"
                f"background-color: rgb{settings.colors['success']}; "
                f"color: rgb(0, 0, 0)}}"
            )
            self.M_over_R.setStyleSheet(style)
        else:
            style = None
        self.M_over_R.setStyleSheet(style)
        self.target_M_over_R.setStyleSheet(style)

    def table_refresh(self):
        """Refresh panel settings/domain table."""
        new_domains: Domains = Domains(
            self.table.fetch_domains(), refs.domains.current.symmetry, self.auto_antiparallel.isChecked()
        )
        # update subunit count and refs.domains.current
        # double-check with user if they want to truncate the domains/subunit count
        # (if that is what they are attempting to do)
        if self.subunit_count.value() < refs.domains.current.subunit.count:
            # helpers.confirm will return a bool
            confirmation: bool = helpers.confirm(
                self.parent(),
                "Subunit Count Reduction",
                f"The prospective subunit count ({self.subunit_count.value()}) is lower than the number of domains in "
                f"the domains table ({self.table.rowCount()}). \n\nAre you sure you want to truncate the "
                f"domains/subunit count to {self.subunit_count.value()}?",
            )
            if confirmation:
                logger.info(
                    "User confirmed that they would like the subunit count reduced."
                )
                new_domains.subunit.count = self.subunit_count.value()
                new_domains.symmetry = self.symmetry.value()
                self.update_table.setStyleSheet(
                    f"background-color: rgb{str(settings.colors['success'])}"
                )
                QTimer.singleShot(
                    600,
                    partial(
                        self.update_table.setStyleSheet, "background-color: light grey"
                    ),
                )
        else:
            new_domains.subunit.count = self.subunit_count.value()
            new_domains.symmetry = self.symmetry.value()

        # update current domains
        refs.domains.current = new_domains

        # refresh table
        self.table.dump_domains(refs.domains.current)
