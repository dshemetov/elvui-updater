"""ElvUI Updater

This script will download and install the latest version of ElvUI. Errors are
logged to run.log.

See python run.py --help for more info.
"""

import logging
import re
import zipfile
from pathlib import Path
from shutil import rmtree
from tempfile import TemporaryFile

import requests
import typer

app = typer.Typer()
logging.basicConfig(
    filename="run.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@app.command()
def update(
    wow_path: Path = typer.Argument(
        ..., help="The path to your WoW folder, e.g. D:/World of Warcraft/ ."
    )
):
    """ElvUI Updater. Say no to more clients!

    Example:
    >>> python elvui_updater.py "D:/World of Warcraft/"
    """

    if not wow_path.exists():
        raise FileNotFoundError(f"The WoW path {wow_path} does not exist.")

    # Get installed ElvUI version.
    elvui_metadata_file = (
        wow_path / "_retail_" / "Interface" / "AddOns" / "ElvUI" / "ElvUI_Mainline.toc"
    )
    if elvui_metadata_file.exists():
        with open(elvui_metadata_file, encoding="utf-8") as f:
            if match := re.search(r"Version: (\d{2}.\d{2})", f.read()):
                installed_elvui_version = match.group(1)
            else:
                raise ValueError(
                    f"Could not find ElvUI version in {elvui_metadata_file}."
                )
    else:
        installed_elvui_version = "0.0"

    # Get latest ElvUI version.
    response = requests.get("https://api.tukui.org/v1/addon/elvui", timeout=10)
    response.raise_for_status()
    json_response = response.json()

    # Check if update is needed.
    logging.info(
        "Installed version: %s. Latest version: %s.",
        installed_elvui_version,
        json_response["version"],
    )
    if installed_elvui_version == json_response["version"]:
        logging.info("Nothing to do.")
        return

    # Download installer, if needed.
    logging.info("Downloading latest version: %s...", json_response["version"])

    with TemporaryFile() as temp_file:
        response = requests.get(json_response["url"], timeout=10)
        response.raise_for_status()
        temp_file.write(response.content)

        # Remove existing installation.
        logging.info("Removing old installation.")
        addons_path = wow_path / "_retail_" / "Interface" / "AddOns"
        elvui_folders = [
            addons_path / "ElvUI",
            addons_path / "ElvUI_Options",
            addons_path / "ElvUI_Libraries",
        ]
        for folder in elvui_folders:
            rmtree(folder, ignore_errors=True)

        # Extract new installation.
        logging.info("Extracting new installation.")
        with zipfile.ZipFile(temp_file) as z:
            z.extractall(addons_path)

    logging.info("Done!")


if __name__ == "__main__":
    try:
        app()
    except Exception as e:  # pylint: disable=broad-except
        logging.exception(e)
