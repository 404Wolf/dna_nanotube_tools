import logging
from collections import namedtuple
from copy import copy
from math import dist
from typing import List, NamedTuple

import settings
from constructor.panels.side_view.plotter import Plotter as Plotter
from constructor.panels.side_view.strand import Strand
from datatypes.misc import Profile
from datatypes.points import NEMid

logger = logging.getLogger(__name__)


class Strands:
    def __init__(self, strands: List[Strand], profile: Profile) -> None:
        """
        Initialize an instance of Strands.

        Args:
            strands: A list of strands to create a Strands object from.
            profile: The settings profile to use for computations.
        """
        assert [isinstance(strand, Strand) for strand in strands]
        self.strands = strands

        assert isinstance(profile, Profile)
        self.profile = profile

    def add_junction(self, NEMid1: NEMid, NEMid2: NEMid) -> None:
        """
        Add a cross-strand junction where NEMid1 and NEMid2 overlap.

        Args:
            NEMid1: One NEMid at the junction site.
            NEMid2: Another NEMid at the junction site.

        Raises:
            ValueError: NEMids are ineligible to be made into a junction.
        """
        if dist(NEMid1.position(), NEMid2.position()) > settings.junction_threshold:
            raise ValueError(
                "NEMids are not close enough to create a junction.",
                NEMid1.position(),
                NEMid2.position()
            )

        # ensure that NEMid1 is the lefter NEMid
        if NEMid1.x_coord > NEMid2.x_coord:
            NEMid1, NEMid2 = NEMid2, NEMid1

        if NEMid1.strand is not NEMid2.strand:
            new_strands = [Strand([], color=(110, 255, 117)), Strand([], color=(250, 145, 255))]

            new_strands[0] = NEMid1.strand[NEMid1.index():]
            new_strands[0] = NEMid2.strand[NEMid2.index():]


            self.strands.remove(NEMid1.strand)
            self.strands.remove(NEMid2.strand)
            self.strands.append(new_strands[0])
            self.strands.append(new_strands[1])

    def ui(self) -> Plotter:
        return Plotter(
            self,
            self.size.width,
            self.size.height,
            self.profile
        )

    @property
    def size(self) -> NamedTuple("Size", width=float, height=float):
        """
        Obtain the size of all strands when laid out.

        Returns:
            tuple(width, height)
        """
        x_coords: List[float] = []
        z_coords: List[float] = []

        for strand in self.strands:
            strand: Strand
            for NEMid_ in strand:
                NEMid_: NEMid
                x_coords.append(NEMid_.x_coord)
                z_coords.append(NEMid_.z_coord)

        return namedtuple("Size", "width height")(
            max(x_coords) - min(x_coords),
            max(z_coords) - min(z_coords)
        )
