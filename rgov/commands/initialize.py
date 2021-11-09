import csv
import os
import urllib.request
import re
import shutil
import zipfile

from cleo import Command
from cleo.helpers import option

from rgov.utils import constants

def cleanhtml(raw_html):
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", raw_html)
    return cleantext


class InitCommand(Command):

    name = "init"
    description = "Update the campground id search index"

    help = """The <info>init</info> command downloads facility data from
recreation.gov and builds a searchable database from that.

By default, the database is built with campground names and ids. The<comment>
--with-descriptions </comment>option includes campground descriptions in the
index, which can be useful for searching for attributes like park name, state,
or city. The size of the database with just names is ~128kb, and is ~9mb with
the descriptions included.

"""

    options = [
        option(
            "with-descriptions",
            "w",
            "Whether to include descriptions in the search database.",
        )
    ]

    def ensure_download_dir_exists(self):
        os.makedirs(constants.download_folder, exist_ok=True)

    def request_ridb_data(self):
        urllib.request.urlretrieve(constants.download_url, constants.download_path)

    def unzip_ridb_data(self):
        with zipfile.ZipFile(constants.download_path, "r") as zip_ref:
            zip_ref.extractall(constants.download_folder)

    def generate_index(self, descriptions):
        """
        Reads from the recreation.gov facilities csv file
        and writes a new csv that includes only the attributes
        that are relevant to the program. This includes
        campground names and ids and optionally, descriptions,
        which provide for better search capabilities but take
        more disk space (around 9mb vs ~130kb). Some data cleaning
        is performed, such as removing html tags and fixing
        capitalization.

        The relevant Recreation.gov facilities csv columns are:
        Column 0 = Facility ID
        Column 5 = Facility Name
        Column 6 = Facility Description
        Column 7 = Facility Type
        Column 19 = Reservable (true or false)

        The output csv is organized as:
        Column 0 = Facility ID
        Column 1 = Facility Name
        Column 2 = Facility Description (if --with-descriptions)
        """
        os.makedirs(constants.data_folder, exist_ok=True)

        with open(constants.facilities_csv_path, "r") as in_file:
            reader = csv.reader(in_file)
            with open(constants.index_path, "w") as out_file:
                writer = csv.writer(out_file)
                for row in reader:
                    # filter for reservable campgrounds with a non-empty name entry
                    if row[7] == "Campground" and row[19] == "true" and row[5]:
                        if descriptions is True:
                            writer.writerow(
                                [row[0], row[5].lower(), cleanhtml(row[6]).lower()]
                            )
                        else:
                            writer.writerow([row[0], row[5].lower()])

    def delete_temp_files(self):
        """
        Removes the project-local downlaod folder
        and its contents.
        """
        shutil.rmtree(constants.download_folder)

    def handle(self):
        descriptions = self.option("with-descriptions")

        steps = [
            ("Ensuring download directory exists", self.ensure_download_dir_exists),
            (f"Downloading data from {constants.download_url}", self.request_ridb_data),
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
            if step[0] == "Generating index":
                step[1](descriptions)  # needs argument
            else:
                step[1]()
            self.overwrite(format + f"<comment>done</comment>.")

        self.line("")
