import dataclasses
import json
from dataclasses import dataclass
from typing import Type, Dict, List
from xlsxwriter.utility import xl_col_to_name


@dataclass(kw_only=True)
class NucleicAcidProfile:
    """
    A container for all geometrical parameters for a nucleic acid.

    Attributes:
        name: The name of the nucleic acid profile.
        D: Diameter of a domain.
        H: Height of a turn.
        g: Nucleoside-Mate Angle.
        T: There are T turns every B bases.
        B: There are B bases every T turns.
        Z_c: Characteristic height.
        Z_mate: Nucleoside-Mate Vertical Distance.
        theta_s: Switch angle.

    Methods:
        update: Update our nucleic_acid_profile in place.
        to_file: Write the nucleic acid nucleic_acid_profile to a file.
        write_worksheet: Write the NucleicAcidProfile to a tab in an Excel document.
    """

    name: str = "MDF B-DNA"

    D: float = 2.2
    H: float = 3.549
    g: float = 134.8
    T: int = 2
    B: int = 21
    Z_c: float = 0.17
    Z_mate: float = 0.094
    theta_s: float = 2.343

    @property
    def Z_b(self) -> float:
        """The base height."""
        return (self.T * self.H) / self.B

    @property
    def theta_b(self) -> float:
        """The base angle."""
        return 360 * (self.T / self.B)

    @property
    def theta_c(self) -> float:
        """The characteristic angle."""
        return 360 / self.B

    def update(self, profile: Type["NucleicAcidProfile"]) -> None:
        """
        Update our nucleic_acid_profile with theirs.

        Updates all of our attributes with the attributes of the given
        nucleic_acid_profile.

        This is useful for updating profiles in-place.
        """
        for attr in self.__dataclass_fields__:
            setattr(self, attr, getattr(profile, attr))

    def to_file(self, filepath: str) -> None:
        """
        Write the nucleic acid nucleic_acid_profile to a file.

        Args:
            filepath: The path to the file to write to.
        """
        with open(filepath, "w") as file:
            json.dump(dataclasses.asdict(self), file, indent=3)

    @classmethod
    def from_file(cls, filepath: str) -> "NucleicAcidProfile":
        """
        Load a NucleicAcidProfile from a file.

        Args:
            filepath: The path to the file to read from.
        """
        with open(filepath, "r") as file:
            return cls(**json.load(file))

    def write_worksheet(
        self,
        workbook,
        name="Nucleic Acid Profile",
        color="#FF6699",
        profiles: List["NucleicAcidProfile"] = None,
    ) -> None:
        """
        Write the NucleicAcidProfile to a tab in an Excel document.

        Args:
            workbook (xlsxwriter.Workbook): The Excel document to write to.
            color: The color of the tab in the Excel document.
            name: The name of the tab in the Excel document.
            profiles: The nucleic acid profiles to write. If None this profile is
                written to the sheet, else the profiles within the list are written.
        """
        profiles = [self] if profiles is None else profiles

        sheet = workbook.add_worksheet(name)
        sheet.set_tab_color(color)

        subscript = workbook.add_format({"font_script": 2})
        comment_scale = {"x_scale": 1.5, "y_scale": 1.5}

        sheet.write(1, 0, "D")
        comment = "The diameter of a given domain in nanometers"
        sheet.write_comment(1, 0, comment, comment_scale)

        description = "The height of one turn of the helical axes in nanometers"
        sheet.write(2, 0, "H")
        sheet.write_comment(2, 0, description, comment_scale)

        description = (
            "The angle about the helical axis between a nucleoside and its "
            "Watson-Crick mate in degrees"
        )
        sheet.write(3, 0, "g")
        sheet.write_comment(3, 0, description, comment_scale)

        description = "There are T turns every B bases"
        sheet.write(4, 0, "T")
        sheet.write_comment(4, 0, description, comment_scale)

        description = "There are T turns every B bases"
        sheet.write(5, 0, "B")
        sheet.write_comment(5, 0, description, comment_scale)

        description = "The height between two NEMids on a given helix"
        sheet.write_rich_string(6, 0, "Z", subscript, "b")
        sheet.write_comment(6, 0, description, comment_scale)

        description = "The height between two NEMids on a given helix"
        sheet.write_rich_string(7, 0, "Z", subscript, "c")
        sheet.write_comment(7, 0, description, comment_scale)

        description = (
            "Vertical distance between a NEMid and its mate on the other helix"
        )
        sheet.write_rich_string(8, 0, "Z", subscript, "mate")
        sheet.write_comment(8, 0, description, comment_scale)

        description = (
            "The smallest angle about the helical axis possible between two NEMids "
            "on the same helix."
        )
        sheet.write_rich_string(9, 0, "θ", subscript, "c")
        sheet.write_comment(9, 0, description, comment_scale)

        description = "The angle about the helical axis between two NEMids"
        sheet.write_rich_string(10, 0, "θ", subscript, "b")
        sheet.write_comment(10, 0, description, comment_scale)

        c = 1
        for profile in profiles:
            column_str = xl_col_to_name(c)

            sheet.write(0, c, profile.name)
            sheet.write(1, c, profile.D)
            sheet.write(2, c, profile.H)
            sheet.write(3, c, profile.g)
            sheet.write(4, c, profile.T)
            sheet.write(5, c, profile.B)
            sheet.write(6, c, f"={column_str}5*{column_str}3/{column_str}6")
            sheet.write(7, c, profile.Z_c)
            sheet.write(8, c, profile.H)
            sheet.write(9, c, f"=360/{column_str}6")
            sheet.write(10, c, f"=360/({column_str}5*{column_str}6)")

            c += 1

    def __eq__(self, other: object) -> bool:
        """
        Whether our nucleic_acid_profile is the same as theirs.

        Checks all of our attributes against theirs.
        """
        if not isinstance(other, NucleicAcidProfile):
            return False

        return all(
            getattr(self, attr) == getattr(other, attr)
            for attr in dataclasses.asdict(self)
        )
