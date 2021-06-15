import click

from .dogstatsd import DogstatsdClient
from .__about__ import __version__

@click.group()
@click.pass_context
@click.version_option(version=__version__, prog_name='dogstatsd-cli')
@click.option('--host', '-h', envvar='DD_AGENT_HOST', default='localhost', help='Host the Datadog Agent is running on')
@click.option('--port', '-p', type=int, default=8125, help='Port DogstatsD server is listening on')
@click.option('--socket', '-s', envvar='DD_DOGSTATSD_SOCKET', help='Unix Domain socket')
def dogstatsd(ctx, host, port, socket):
    """
    A command line interface for sending metrics, events and 
    service checks to the Datadog Agent's DogstatsD server.
    """
    ctx.ensure_object(dict)
    ctx.obj['client'] = DogstatsdClient(
        host, 
        port,
        socket
        )

    if ctx.invoked_subcommand is None:
        click.echo('I was invoked without subcommand')
    else:
        click.echo(f"I am about to invoke {ctx.invoked_subcommand}")



@dogstatsd.command()
@click.pass_context
@click.option('--name', '-n', required=True, help='Metric name')
@click.option('--value', '-v', required=True, type=float, help='Metric value')
@click.option('--operation', '-o', required=True, type=click.Choice([
    'increment',
    'decrement',
    'count', 
    'gauge',
    'set',
    'histogram',
    'timed',
    'distribution'
    ]), help='Metric operation')
@click.option('--sample-rate', '-s', type=float, help='Sample rate')
@click.option('--tags', '-t', help='Comma separated list of tags')
def metric(ctx, name, value, operation, sample_rate, tags):
    print(tags)
    client = ctx.obj['client']
    client.metric(name, value, operation, sample_rate, tags)


@dogstatsd.command()
@click.pass_context
@click.option('--name', '-n', required=True, help='Metric name')
@click.option('--status', '-s', required=True, type=click.Choice([str(n) for n in range(4)]), help='Status')
@click.option('--date', '-d', help='Unix timestamp')
@click.option('--hostname', '-h', help='hostname')
@click.option('--tags', '-t', help='Comma separated list of tags')
@click.option('--message', '-m', help='A message describing the current state of the service check')
def service_check(ctx, name, status, date, hostname, tags, message):
    client = ctx.obj['client']
    client.service_check(name, status, date, hostname, tags, message)


@dogstatsd.command()
@click.pass_context
@click.option('--title', '-ti', required=True, help='Event title')
@click.option('--text', '-tx', required=True, help='Event text')
@click.option('--date', '-d', help='timestamp')
@click.option('--hostname', '-h', help='Hostname')
@click.option('--aggregation-key', '-a', help='Hostname')
@click.option('--priority', '-p', help='Priority')
@click.option('--alert-type', '-at', type=click.Choice([
    'error', 
    'warning', 
    'info',
    'success']), help='Alert type')
@click.option('--source-type-name', '-s', help='Alert type')
@click.option('--tags', '-t', help='Comma separated list of tags')
def event(ctx, title, text, date, hostname, aggregation_key, priority, alert_type, source_type_name, tags):
    client = ctx.obj['client']
    client.event(title, text, date, hostname, aggregation_key, priority, alert_type, source_type_name, tags)
