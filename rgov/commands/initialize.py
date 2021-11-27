import csv
import os
import urllib.request
import re
import shutil
import zipfile

from cleo import Command
from cleo.helpers import option

from rgov import locations, pushsafer


def cleanhtml(raw_html) -> str:
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", raw_html)
    return cleantext


class InitCommand(Command):

    _DOWNLOAD_URL = "https://ridb.recreation.gov/downloads/RIDBFullExport_V1_CSV.zip"

    name = "init"
    description = "Update the campground id search index"

    help = """The <question>init</> command is for rebuilding the campground database, which is a csv file of campground names, ids, and optionally their corresponding descriptions. Running this command is only necessary if there is a problem with the existing database or it needs to be updated.  

<options=bold>Examples:</>

Download and (re)build the campground databse:

    $ <info>poetry run rgov init</>
"""

    def ensure_download_dir_exists(self):
        os.makedirs(locations.DOWNLOAD_FOLDER, exist_ok=True)

    def request_ridb_data(self):
        urllib.request.urlretrieve(self._DOWNLOAD_URL, locations.DOWNLOAD_PATH)

    def unzip_ridb_data(self):
        with zipfile.ZipFile(locations.DOWNLOAD_PATH, "r") as zip_ref:
            zip_ref.extractall(locations.DOWNLOAD_FOLDER)

    def generate_index(self):
        """
        Reads from the recreation.gov facilities csv file
        and writes a new csv that includes only the attributes
        that are relevant to the program. This includes
        campground names, ids, and descriptions. 
        
        The relevant Recreation.gov facilities csv columns are:
        Column 0 = Facility ID
        Column 5 = Facility Name
        Column 6 = Facility Description
        Column 7 = Facility Type
        Column 19 = Reservable (true or false)

        The output csv is organized as:
        Column 0 = Facility ID
        Column 1 = Facility Name
        Column 2 = Facility Description 
        """
        os.makedirs(locations.DATA_FOLDER, exist_ok=True)
        facilities_list = []
        with open(locations.FACILITIES_CSV_PATH, "r") as in_file:
            reader = csv.reader(in_file)
            for row in reader:
                # filter for reservable campgrounds with a non-empty name entry
                if row[7] == "Campground" and row[19] == "true" and row[5]:
                    facilities_list.append(
                        [row[0], row[5].lower(), cleanhtml(row[6]).lower()]
                    )
        # sort the entries alphabetically by name so search results are
        # also alphabetical
        facilities_list.sort(key=lambda x: x[1])
        with open(locations.INDEX_PATH, "w") as out_file:
            writer = csv.writer(out_file)
            for row in facilities_list:
                writer.writerow(row)

    def delete_temp_files(self):
        """
        Removes the project-local downlaod folder
        and its contents.
        """
        shutil.rmtree(locations.DOWNLOAD_FOLDER)

    def handle(self) -> int:
        steps = [
            ("Checking download directory", self.ensure_download_dir_exists),
            (f"Downloading data from {self._DOWNLOAD_URL}", self.request_ridb_data),
            ("Unzipping", self.unzip_ridb_data),
            ("Generating index", self.generate_index),
            ("Deleting temporary files", self.delete_temp_files),
        ]

        if not self.confirm(
            "Continue with downloading and generating the campsite id index?", False
        ):
            return

        for step in steps:
            format = f"<question>{step[0]}...</question>"
            self.line("")
            self.write(format)
            step[1]()
            self.overwrite(format + f"<comment>done</comment>.")

        self.line("")
        return 0
