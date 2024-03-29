import logging
import click

from .dogstatsd import DogstatsdClient, SERVICE_CHECK_STATUSES
from .__about__ import __version__
from .logger import setup_logger

@click.group()
@click.pass_context
@click.option('--verbose', '-v', is_flag=True, help="Display verbose output")
@click.option('-host', '-h', envvar='DD_AGENT_HOST', default='localhost', help='Host the Datadog Agent is running on')
@click.option('-port', '-p', envvar='DD_AGENT_PORT', type=int, default=8125, help='Port DogstatsD server is listening on')
@click.option('-socket', '-s', envvar='DD_DOGSTATSD_SOCKET', help='Unix Domain socket')
@click.version_option(version=__version__, prog_name='dogstatsd-cli')
def dogstatsd(ctx, host, port, socket, verbose):
    """
    A command line interface for sending metrics, events and 
    service checks to the Datadog Agent's DogstatsD server.
    """
    logger = setup_logger(level=logging.DEBUG if verbose else logging.INFO)
    
    ctx.ensure_object(dict)
    ctx.obj['client'] = DogstatsdClient(host, port, socket)
    ctx.obj['logger'] = logger




@dogstatsd.command()
@click.pass_context
@click.argument('name')
@click.argument('value', default=1)
@click.option('-sample-rate', '-s', type=float, help='Sample rate')
@click.option('-tags', '-t', multiple=True, help='Comma separated list of tags')
def increment(ctx, name, value, sample_rate, tags):
    """
    Increment a metric by a specific value\n
    NAME metric name\n
    VALUE metric value
    """
    client = ctx.obj['client']
    client.increment(name, value, sample_rate, tags)

@dogstatsd.command()
@click.pass_context
@click.argument('name')
@click.argument('value', default=1)
@click.option('-sample-rate', '-s', type=float, help='Sample rate')
@click.option('-tags', '-t', multiple=True, help='Comma separated list of tags')
def decrement(ctx, name, value, sample_rate, tags):
    """
    Decrement a metric by a specific value\n
    NAME metric name\n
    VALUE metric value
    """
    client = ctx.obj['client']
    client.decrement(name, value, sample_rate, tags)

@dogstatsd.command()
@click.pass_context
@click.argument('name')
@click.argument('value')
@click.option('-sample-rate', '-s', type=float, help='Sample rate')
@click.option('-tags', '-t', multiple=True, help='Comma separated list of tags')
def count(ctx, name, value, sample_rate, tags):
    """
    Send a count type metric\n
    NAME metric name\n
    VALUE metric value
    """
    client = ctx.obj['client']
    client.count(name, value, sample_rate, tags)

@dogstatsd.command()
@click.pass_context
@click.argument('name')
@click.argument('value')
@click.option('-sample-rate', '-s', type=float, help='Sample rate')
@click.option('-tags', '-t', multiple=True, help='Comma separated list of tags')
def gauge(ctx, name, value, sample_rate, tags):
    """
    Send a gauge type metric\n
    NAME metric name\n
    VALUE metric value
    """
    client = ctx.obj['client']
    client.gauge(name, value, sample_rate, tags)

@dogstatsd.command()
@click.pass_context
@click.argument('name')
@click.argument('value')
@click.option('-sample-rate', '-s', type=float, help='Sample rate')
@click.option('-tags', '-t', multiple=True, help='Comma separated list of tags')
def set(ctx, name, value, sample_rate, tags):
    """
    Send a set type metric\n
    NAME metric name\n
    VALUE metric value
    """
    client = ctx.obj['client']
    client.set(name, value, sample_rate, tags)

@dogstatsd.command()
@click.pass_context
@click.argument('name')
@click.argument('value')
@click.option('-sample-rate', '-s', type=float, help='Sample rate')
@click.option('-tags', '-t', multiple=True, help='Comma separated list of tags')
def histogram(ctx, name, value, sample_rate, tags):
    """
    Send a histogram type metric\n
    NAME metric name\n
    VALUE metric value
    """
    client = ctx.obj['client']
    client.histogram(name, value, sample_rate, tags)

@dogstatsd.command()
@click.pass_context
@click.argument('name')
@click.argument('value')
@click.option('-sample-rate', '-s', type=float, help='Sample rate')
@click.option('-tags', '-t', multiple=True, help='Comma separated list of tags')
def timer(ctx, name, value, sample_rate, tags):
    """
    Send a timer type metric\n
    NAME metric name\n
    VALUE metric value
    """
    client = ctx.obj['client']
    client.timer(name, value, sample_rate, tags)

@dogstatsd.command()
@click.pass_context
@click.argument('name')
@click.argument('value')
@click.option('-sample-rate', '-s', type=float, help='Sample rate')
@click.option('-tags', '-t', multiple=True, help='Comma separated list of tags')
def distribution(ctx, name, value, sample_rate, tags):
    """
    Send a distribution type metric\n
    NAME metric name\n
    VALUE metric value
    """
    client = ctx.obj['client']
    client.distribution(name, value, sample_rate, tags)

@dogstatsd.command()
@click.pass_context
@click.argument('name')
@click.argument('status', type=click.Choice(SERVICE_CHECK_STATUSES))
@click.option('-date', '-d', help='Unix timestamp')
@click.option('-hostname', '-h', help='Hostname')
@click.option('-tags', '-t', multiple=True, help='Comma separated list of tags')
@click.option('-message', '-m', help='A message describing the current state of the service check')
def service_check(ctx, name, status, date, hostname, tags, message):
    """
    Send a service check\n
    NAME service-check name\n
    STATUS a number mapping betweek 0-3
    """
    client = ctx.obj['client']
    client.service_check(name, status, date, hostname, tags, message)


@dogstatsd.command()
@click.pass_context
@click.argument('title')
@click.argument('text')
@click.option('-date', '-d', help='Unix timestamp')
@click.option('-hostname', '-h', help='Hostname')
@click.option('-aggregation-key', '-a', help='Aggregation key')
@click.option('-priority', '-p', help='Priority')
@click.option('-alert-type', '-at', type=click.Choice([
    'error', 
    'warning', 
    'info',
    'success']), help='Alert type')
@click.option('-source-type-name', '-s', help='Alert type')
@click.option('-tags', '-t', multiple=True, help='Comma separated list of tags')
def event(ctx, title, text, date, hostname, aggregation_key, priority, alert_type, source_type_name, tags):
    """
    Send an event\n
    TITLE the title of the event\n
    MESSAGE the event's message
    """
    client = ctx.obj['client']
    client.event(title, text, date, hostname, aggregation_key, priority, alert_type, source_type_name, tags)
