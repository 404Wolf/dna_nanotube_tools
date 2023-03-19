import logging
from uuid import uuid1

import pandas as pd

from constants.directions import DOWN, UP
from structures.helices.helix import Helix
from utils import inverse

logger = logging.getLogger(__name__)


class DoubleHelix:
    """
    A container storing the two helices of a double helix.

    This class lets you reference a given helix by its zeroedness (zeroed or other),
    direction (up or down), or domain helical joint (left or right).

    Attributes:
        zeroed_helix: The helix that is lined up with the previous double helix on
            the left side. The opposite helix is the "other helix".
        other_helix: The other helix in the same domain as the zeroed helix. This is,
            by definition, the helix that is not the zeroed helix.
        up_helix: The helix that has progresses upwards from its 5' to 3' end of the
            strand. This is also known as the up helix.
        down_helix: The helix that has progresses downwards from its 5' to 3' end of
            the strand. This is also known as the down helix.
        left_helix: The helix that is of the direction of the domain's left helical
            joint. This is the helix whose points are lined up to the points that are
            on the helix of the previous domain's right helical joint helix.
        right_helix: The helix that is of the direction of the domain's right helical
            joint. This is the helix whose points are lined up to the points that are
            on the helix of the next domain's left helical joint helix.
        uuid: The UUID of the double helix. This is automatically generated when the
            double helix is created.

    Methods:
        to_csv: Write the double helix to a CSV file.
    """

    __slots__ = "domain", "helices", "uuid"

    def __init__(
        self,
        domain: "Domain",
        up_helix: Helix | None = None,
        down_helix: Helix | None = None,
        uuid: str | None = None,
        resize_helices: bool = True,
    ) -> None:
        """
        Initialize a double helix.

        Args:
            domain: The domain that the double helix is in.
            up_helix: The helix that progresses upwards from its 5' to 3' end. If
                None, a new and empty helix will be created.
            down_helix: The helix that progresses downwards from its 5' to 3' end. If
                None, a new and empty helix will be created.
            uuid: The UUID of the double helix. If None, a new UUID will be created.
            resize_helices: Whether to resize the helices to the size of the domain's
                GenerationCount.
        """
        self.domain = domain
        self.helices = [None, None]
        self.uuid = uuid or str(uuid1())

        if up_helix is not None:
            logger.debug("Using passed up helix.")
            if up_helix.direction != UP:
                raise ValueError("The up helix must be of the UP direction.")
            self.helices[UP] = up_helix
            self.helices[UP].double_helix = self
        else:
            logger.debug("Creating new up helix since None was passed.")
            self.helices[UP] = Helix(direction=UP, double_helix=self)

        if down_helix is not None:
            logger.debug("Using passed down helix.")
            if down_helix.direction != DOWN:
                raise ValueError("The down helix must be of the DOWN direction.")
            self.helices[DOWN] = down_helix
            self.helices[DOWN].double_helix = self
        else:
            logger.debug("Creating new down helix since None was passed.")
            self.helices[DOWN] = Helix(direction=DOWN, double_helix=self)

        if resize_helices:
            # The helices must contain empty arrays of the size that the Domains
            # indicates.
            self.left_helix.data.resize(self.domain.left_helix_count)
            self.other_helix.data.resize(self.domain.other_helix_count)

    def __getitem__(self, index: int) -> Helix:
        """
        Get a helix in the double helix.

        Args:
            index: The index of the helix to get. This can be either UP or DOWN. UP
                or DOWN are constants that are defined in the constants.directions
                module, and are 0 and 1, respectively.

        Returns:
            The helix at the given index.
        """
        return self.helices[index]

    @property
    def left_helix(self) -> Helix:
        """
        The helix that is on the left side of the domain and is thus lined up with
        the previous domain's right helical joint.
        """
        return self.helices[self.domain.left_helix_joint]

    @property
    def right_helix(self) -> Helix:
        """
        The helix that is on the right side of the domain and is thus lined up with the
        next domain's left helical joint.
        """
        return self.helices[self.domain.right_helix_joint]

    @property
    def up_helix(self) -> Helix:
        """
        The helix that has progresses upwards from its 5' to 3' ends.
        """
        return self.helices[UP]

    @property
    def down_helix(self) -> Helix:
        """
        The helix that has progresses downwards from its 5' to 3' ends.
        """
        return self.helices[DOWN]

    @property
    def zeroed_helix(self) -> Helix:
        """
        The helix that is lined up with the previous double helix on the left side.
        """
        return self.helices[self.domain.left_helix_joint]

    @property
    def other_helix(self) -> Helix:
        """
        The other helix in the same domain as the zeroed helix.
        """
        return self.helices[inverse(self.domain.left_helix_joint)]


def to_df(double_helices) -> pd.DataFrame:
    """
    Obtain a pandas dataframe of many double helices.

    Returns:
        A pandas dataframe containing many double helices.
    """
    data = {"uuid": [], "data:domain": [], "data:up_helix": [], "data:down_helix": []}

    for double_helix in double_helices:
        data["uuid"].append(double_helix.uuid)
        data["data:domain"].append(double_helix.domain.uuid)
        data["data:up_helix"].append(double_helix.up_helix.uuid)
        data["data:down_helix"].append(double_helix.down_helix.uuid)

    return pd.DataFrame(data)
