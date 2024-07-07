"""Holds utilities for other sections"""

import typing


class LinkableClass:
    """Base class for anything that is linkable"""

    linked_list: list["LinkableClass"]
    previous_section: "LinkableClass"
    next_section: "LinkableClass"

    def link_up(
        self,
        previous_section: typing.Self | None = None,
        next_section: typing.Self | None = None,
    ) -> None:
        """Links up the chain"""

        self.previous_section = previous_section
        self.next_section = next_section
