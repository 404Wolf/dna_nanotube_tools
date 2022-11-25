from typing import Iterable

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from .display_area import DisplayArea
from .editor_area import EditorArea


class UserInputSequenceEditor(QWidget):
    base_reset: pyqtSignal
    base_unset: pyqtSignal
    base_set: pyqtSignal

    def __init__(self, bases: Iterable):
        super().__init__()
        self.setWindowTitle("Sequence Editor")
        self._bases = list(bases)

        if len(self.bases) > 1000:
            raise OverflowError("Too many bases for manual input sequence editor!")

        self.setLayout(QVBoxLayout())

        # run setup functions
        self._display_area()
        self._editor_area()
        self._signals()
        self._prettify()

        # wrap signals from self.editor_area
        self.base_reset = self.editor_area.base_reset
        self.base_unset = self.editor_area.base_unset
        self.base_set = self.editor_area.base_set

    @property
    def bases(self):
        """Obtain all bases contained within."""
        return self._bases

    @bases.setter
    def bases(self, bases):
        self._bases = bases
        self.refresh()

    def refresh(self):
        # update the display area
        self.display_area.blockSignals(True)
        self.display_area.bases = self.editor_area.bases
        self.display_area.highlight(self.editor_area.selected)
        self.display_area.blockSignals(False)

    def _prettify(self):
        self.setMinimumWidth(650)
        self.setFixedHeight(400)
        self.scrollable_editor_area.setFixedHeight(100)

    def _signals(self):
        def editor_area_updated():
            if self.bases != self.editor_area.bases:
                self.bases = self.editor_area.bases

        def editor_area_shifted_right(index: int = 0):
            widget = self.editor_area.widgets[index]
            scroll_bar = self.scrollable_editor_area.horizontalScrollBar()
            scroll_bar.setValue(scroll_bar.value() + widget.width())

        def editor_area_shifted_left(index: int = 0):
            widget = self.editor_area.widgets[index]
            scroll_bar = self.scrollable_editor_area.horizontalScrollBar()
            scroll_bar.setValue(scroll_bar.value() - widget.width())

        def editor_area_selection_changed(previous_index: int, new_index: int):
            self.display_area.blockSignals(True)
            self.display_area.highlight(new_index)
            self.display_area.blockSignals(False)
            # shift the editor area
            if new_index > previous_index:
                editor_area_shifted_right()
            else:
                editor_area_shifted_left()

        self.editor_area.base_set.connect(editor_area_shifted_right)
        self.editor_area.base_reset.connect(editor_area_shifted_right)
        self.editor_area.base_unset.connect(editor_area_shifted_left)
        self.editor_area.updated.connect(editor_area_updated)
        self.editor_area.selection_changed.connect(editor_area_selection_changed)

    def _editor_area(self):
        """Create the base editor area."""
        self.editor_area = EditorArea(self, self.bases)

        self.scrollable_editor_area = QScrollArea()
        self.scrollable_editor_area.setWidget(self.editor_area)
        self.scrollable_editor_area.setWidgetResizable(True)
        self.scrollable_editor_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scrollable_editor_area.setStyleSheet(
            """
            QScrollArea{
                border: 1px solid rgb(170, 170, 170);
            }
        """
        )

        self.layout().addWidget(self.scrollable_editor_area)

    def _display_area(self):
        """Create the sequence viewer area."""
        self.display_area = DisplayArea(self, self.bases)
        self.layout().addWidget(self.display_area)
