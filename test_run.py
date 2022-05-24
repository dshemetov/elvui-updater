from typer.testing import CliRunner

from run import app

runner = CliRunner()


def test_app():
    result = runner.invoke(app, ["D:/World of Warcraft/"])
    assert result.exit_code == 0


test_app()
