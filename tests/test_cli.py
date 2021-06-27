from click.testing import CliRunner
from dogstatsd_cli import dogstatsd

def test_dogstatsd_cli():
    runner = CliRunner
    result = runner.invoke(dogstatsd, ['-v'])
    assert result.exit_code == 0