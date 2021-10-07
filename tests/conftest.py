from dogstatsd_cli.dogstatsd import DogstatsdClient
import pytest
from click.testing import CliRunner
from dogstatsd_cli.dogstatsd import DogstatsdClient

@pytest.fixture
def dogstatsd_client_default_instance():
    return DogstatsdClient()


@pytest.fixture
def runner():
    yield CliRunner()
