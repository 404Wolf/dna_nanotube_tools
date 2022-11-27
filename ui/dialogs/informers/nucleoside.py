from PyQt6 import uic
from PyQt6.QtWidgets import QDialog

from constants.directions import *
from structures.domains import Domains
from structures.points import NEMid, Nucleoside
from structures.strands import Strands


class NucleosideInformer(QDialog):
    def __init__(
        self, parent, nucleoside: Nucleoside, all_strands: Strands, all_domains: Domains
    ):
        super().__init__(parent)
        assert isinstance(all_strands, Strands)
        assert isinstance(all_domains, Domains)
        assert isinstance(nucleoside, Nucleoside)

        self.setWindowTitle("Nucleoside Information")
        uic.loadUi("ui/dialogs/informers/nucleoside.ui", self)

        self.x_coordinate.setText(f"{nucleoside.x_coord:.4f} nanometers")
        self.z_coordinate.setText(f"{nucleoside.z_coord:.4f} nanometers")
        self.angle.setText(f"{nucleoside.angle:.4f}°")

        strand_index = all_strands.index(nucleoside.strand)
        if nucleoside.strand.closed:
            openness = "closed"
        else:  # not item.strand.closed
            openness = "open"
        self.strand.setText(
            f"item #{nucleoside.index + 1} in {openness} strand #{strand_index}"
        )

        self.original_domain.setText(
            f"domain #{nucleoside.domain.index + 1} of {all_domains.count} domains"
        )

        if nucleoside.direction == UP:
            self.up.setChecked(True)
        elif nucleoside.direction == DOWN:
            self.down.setChecked(True)

        style = (
            "QTextEdit{{"
            "color: rgb(0, 0, 0); "
            "font-size: {font_size}px; "
            "text-align: center; "
            "background: rgb(255, 255, 255)"
            "}};"
        )
        if nucleoside.base is None:
            self.base.setStyleSheet(style.format(font_size=10))
            self.base.setText("Unset\nBase")
        else:
            self.base.setStyleSheet(style.format(font_size=32))
            self.base.setText(nucleoside.base)
