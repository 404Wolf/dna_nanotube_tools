import random

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QFileDialog

import helpers
from constants.bases import DNA


class BulkInputSequenceEditor(QWidget):
    def __init__(self, parent, bases):
        super().__init__(parent)
        uic.loadUi("ui/dialogs/sequence_editor/bulk_input/panel.ui", self)

        self._bases = bases

        self._from_file()
        self._randomize_sequence()
        self._clear_sequence()

    @property
    def bases(self):
        return self._bases

    @bases.setter
    def bases(self, new_bases):
        self._bases = new_bases
        self.sequence_display.setPlainText("".join(self.bases))

    def _from_file(self):
        def from_file_clicked():
            # obtain filepath from user
            filepath = QFileDialog.getOpenFileName(
                self, "Choose File Location", filter="*.txt"
            )[0]
            # open and load file
            with open(filepath) as file:
                file_bases = file.read()
            # remove blank characters
            file_bases = "".join(file_bases.split())

            # make sure that the file doesn't contain more bases than we are allowed to have
            # (or if it does get confirmation of user)
            if len(file_bases) > len(self.bases):
                difference = len(file_bases) - len(self.bases)
                confirmed = helpers.confirm(
                    self.parent(),
                    "Sequence Overload",
                    f"The chosen file contains {difference} more bases than the strand allows for. If you proceed the "
                    f"inputted bases will be truncated to the strand length. \n\n Would you like to proceed?",
                )
                file_bases = file_bases[: len(self.bases)]
            else:
                # if the amount of bases in the file is reasonable proceed as normal
                confirmed = True

            # if ready, build the new list of bases
            if confirmed:
                bases = []
                for file_base in file_bases:
                    if file_base.upper() not in DNA:
                        # if any base is of the wrong type then cancel the operation
                        helpers.warning(
                            self.parent(),
                            "Invalid bases",
                            "This file contains invalid base characters!\n"
                            f"The file must only consist of {str(DNA)}.",
                        )
                        return
                    else:
                        bases.append(file_base.upper())

                # update our bases with the new ones loaded from the file
                self.bases = bases

        self.import_file.clicked.connect(from_file_clicked)

    def _randomize_sequence(self):
        def randomize_sequence_clicked():
            self.bases = [random.choice(DNA) for _ in range(len(self.bases))]

        self.randomize_sequence.clicked.connect(randomize_sequence_clicked)

    def _clear_sequence(self):
        def clear_sequence_clicked():
            self.bases = []

        self.clear_sequence.clicked.connect(clear_sequence_clicked)