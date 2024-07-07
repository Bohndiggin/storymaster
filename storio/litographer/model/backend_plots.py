"""File to contain the plot related sections"""

import enum

from storio.model.database import schema
from storio.litographer.model import backend_nodes, utilities


class PlotSection(utilities.LinkableClass):
    """Plot section is the class to manage the sections of the plot. It holds the nodes"""

    section_name: str
    section_type: schema.PlotSectionType
    nodes: list[backend_nodes.BaseNode]


class ExpositionSection(PlotSection):
    """Section of the plot that lays groundwork for the story."""

    section_name = "Exposition"
    section_type = schema.PlotSectionType.FLAT


class IncitingIncidentSection(PlotSection):
    """Section of the plot that starts the action in the story."""

    section_name = "Inciting Incident"
    section_type = schema.PlotSectionType.POINT


class RisingActionSection(PlotSection):
    """Section of the plot that the action ramps up, longest in story"""

    section_name = "Rising Action"
    section_type = schema.PlotSectionType.RISING


class ClimaxSection(PlotSection):
    """Section of the plot at the height of the action. The tipping point of the story."""

    section_name = "Climax"
    section_type = schema.PlotSectionType.POINT


class FallingActionSection(PlotSection):
    """Section of the plot where things are being resolved."""

    section_name = "Falling Action"
    section_type = schema.PlotSectionType.LOWER


class ResolutionSection(PlotSection):
    """Section of the plot where things are wrapped up"""

    section_name = "Resolution"
    section_type = schema.PlotSectionType.FLAT


class BasePlotType:
    """Base Plot Type is the parent class for the different plot types. Made up of plot sections"""

    plot_name: str
    plot_list: list[PlotSection]


class AristotelianPlot(BasePlotType):
    """Aristotelian Plot"""

    plot_name = "Aristotelian"

    def __init__(self) -> None:
        self.exposition = ExpositionSection()
        self.inciting_incident = IncitingIncidentSection()
        self.rising_action = RisingActionSection()
        self.climax = ClimaxSection()
        self.falling_action = FallingActionSection()
        self.resolution = ResolutionSection()

        self.plot_list = [
            self.exposition,
            self.inciting_incident,
            self.rising_action,
            self.climax,
            self.falling_action,
            self.resolution,
        ]

        self.exposition.link_up(next_section=self.inciting_incident)
        self.inciting_incident.link_up(self.exposition, self.rising_action)
        self.rising_action.link_up(self.inciting_incident, self.climax)
        self.climax.link_up(self.rising_action, self.falling_action)
        self.falling_action.link_up(self.climax, self.resolution)
        self.resolution.link_up(previous_section=self.falling_action)
