from typer.testing import CliRunner

from ctfdl.cli.main import app

runner = CliRunner()


def test_help_command_runs():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output
