##################################################################################
# update_elvui.py
#
# ElvUI Updater
#
# (For the lazy or those who refuse to download more clients.)
#
# Usage:
#
# python update_elvui.py -w <World of Warcraft Path>
#
# e.g.
#
# python update_elvui.py -w "D:\World of Warcraft\"
#
# Place it in a .bat file and use Task Scheduler to automate daily.
#
##################################################################################

import argparse
import logging
from os.path import basename, dirname, exists, join
import re
from shutil import rmtree
import zipfile

from bs4 import BeautifulSoup
import requests


class ElvUIUpdater:
    def __init__(self, wow_path: str, elvui_url: str = "https://www.tukui.org/download.php?ui=elvui", download_path: str = ".", logfile: str = "update_elvui.log", loglevel: int = logging.INFO):
        self.wow_path = wow_path
        self.elvui_url = elvui_url
        self.download_path = download_path
        self.logger = self._setup_logger(logfile, loglevel)

        try:
            if not exists(self.wow_path):
                raise FileNotFoundError("The WoW path seems to be wrong.")
            if not exists(self.download_path):
                raise FileNotFoundError("The ElvUI archive path seems to be wrong.")

            self.installed_elvui_version = self.get_elvui_version(self.wow_path)
            self.latest_elvui_download_url = self._scrape_latest_download_url(self.elvui_url)
            self.latest_elvui_version = re.search(r"(\d{2}.\d{2})", self.latest_elvui_download_url).group(0)
        except Exception as e:
            self.logger.exception(e)
            raise e

    @staticmethod
    def _setup_logger(logfile: str, loglevel: int = logging.INFO) -> logging.Logger:
        logger = logging.getLogger("ElvUI_FileLogger")
        logger.setLevel(loglevel)
        fh = logging.FileHandler(logfile)
        fh.setLevel(loglevel)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        return logger

    @staticmethod
    def _scrape_latest_download_url(elvui_url: str) -> str:
        res = requests.get(elvui_url)
        html_soup = BeautifulSoup(res.text, "html.parser")
        for link in html_soup.find_all("a"):
            relative_path = link.get("href")
            if relative_path and ".zip" in relative_path:
                latest_elvui_download_url = f"{dirname(elvui_url)}{relative_path}"
                break
        return latest_elvui_download_url

    @staticmethod
    def _download_zip(url: str, download_path: str):
        zip_name = join(download_path, basename(url))
        with open(zip_name, "wb") as f:
            f.write(requests.get(url).content)

    def get_elvui_version(self, wow_path: str) -> str:
        try:
            with open(join(wow_path, "_retail_", "Interface", "AddOns", "ElvUI", "ElvUI_Mainline.toc")) as f:
                return re.search(r"Version: (\d{2}.\d{2})", f.read()).group(1)
        except FileNotFoundError:
            self.logger.info("Currently installed ElvUI version not found.")
            return "0.0"

    @staticmethod
    def install_elvui(latest_elvui_version: str, wow_path: str):
        # Remove existing ElvUI installation
        rmtree(join(wow_path, "_retail_", "Interface", "AddOns", "ElvUI"), ignore_errors=True)
        rmtree(join(wow_path, "_retail_", "Interface", "AddOns", "ElvUI_OptionsUI"), ignore_errors=True)

        # Extract the new ElvUI installation
        with zipfile.ZipFile(f"elvui-{latest_elvui_version}.zip") as z:
            z.extractall(path=join(wow_path, "_retail_", "Interface", "AddOns"))

    def install(self):
        try:
            if self.installed_elvui_version == self.latest_elvui_version:
                self.logger.info(f"Already at latest version: {self.latest_elvui_version}.\n")
            else:
                if not exists(join(self.download_path, f"elvui-{self.latest_elvui_version}.zip")):
                    self.logger.info(f"Downloading latest version: {self.latest_elvui_version}...\n")
                    self._download_zip(self.latest_elvui_download_url, path=self.download_path)
                else:
                    self.logger.info(f"Latest version already downloaded: elvui-{self.latest_elvui_version}.zip!\n")
                self.logger.info(f"Installing...\n")
                self.install_elvui(self.latest_elvui_version, self.wow_path)
                self.logger.info(f"Done!\n")
        except Exception as e:
            self.logger.exception(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update your ElvUI.")
    parser.add_argument("-w", "--wow-path", dest="wow_path", type=str, action="store", required=True, help="The path to your WoW folder, e.g. 'D:\World of Warcraft'.")
    parser.add_argument("-e", "--download-path", dest="download_path", type=str, action="store", default=".", help="The path where you want to store the elvui zip files.")
    args = parser.parse_args()
    args.wow_path = args.wow_path.strip("\"'")

    installer = ElvUIUpdater(wow_path = args.wow_path, download_path = args.download_path)
    installer.install()
