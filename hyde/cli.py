import click
from click import Context

from hyde import Hyde


@click.group()
@click.pass_context
def cli(ctx: Context) -> None:
    ctx.ensure_object(dict)
    hyde = Hyde()
    ctx.obj['hyde'] = hyde


@cli.command('build')
@click.pass_context
def build(ctx: Context) -> None:
    hyde: Hyde = ctx.obj['hyde']
    hyde.generate_site()


@cli.command('clean')
@click.pass_context
def clean(ctx: Context) -> None:
    hyde: Hyde = ctx.obj['hyde']
    hyde.clean_site()
