"""Test file for litographer_model"""

from unittest.mock import MagicMock, patch
import pytest
from faker import Faker

from storio.model.database.schema.base import NoteType
from storio.model.litographer.litographer_model import LitographerPlotNodeModel

fake = Faker()

class TestLitographerPlotNodeModel:
    """Test class for LitographerPlotNodeModel"""

    @pytest.fixture(scope="class")
    @patch("storio.model.litographer.litographer_model.BaseModel")
    @patch("storio.model.litographer.litographer_model.Session")
    def model(self, mock_session:MagicMock, mock_base: MagicMock) -> LitographerPlotNodeModel:
        return LitographerPlotNodeModel(MagicMock(), MagicMock(), MagicMock(), MagicMock())


    # @patch("storio.model.litographer.litographer_model.Session")
    def test_init(self, model: LitographerPlotNodeModel) -> None:
        """Tests _gather_self first with one that works, then with one that doesn't"""

        model.engine
        print('huh')

        

        

        
        

        



