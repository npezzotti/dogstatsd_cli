from dogstatsd_cli.cli import dogstatsd


def test_metrics(runner):
    sub_commands = {
        'count',
        'decrement',
        'distribution',
        'gauge',
        'histogram',
        'increment',
        'set',
        'timer',
    }

    for command in sub_commands:
        result = runner.invoke(dogstatsd, [command, 'test', '1'])
        
        assert result.exit_code == 0


def test_event(runner):
    result = runner.invoke(dogstatsd, ['event', 'test', 'test'])
    
    assert result.exit_code == 0


def test_service_check(runner):
    result = runner.invoke(dogstatsd, ['service-check', 'test', '0'])

    assert result.exit_code == 0
    print(result.output)


def test_invalid_value_port(runner):
    expected = (
        "Error: Invalid value for '-port' / '-p': 'test' is not a valid integer."
    )

    result = runner.invoke(dogstatsd, ['-p', 'test'])

    assert result.exit_code == 2 
    assert 'Usage: dogstatsd' in result.output
    assert expected in result.output
