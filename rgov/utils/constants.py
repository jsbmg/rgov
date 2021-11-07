from os.path import join
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).parent.parent

project_root = get_project_root()
download_url = "https://ridb.recreation.gov/downloads/RIDBFullExport_V1_CSV.zip"
download_folder = join(project_root, "assets")
download_path = join(download_folder, "RIDBExport.zip")
facilities_csv_path = join(download_folder, "Facilities_API_v1.csv")
data_folder = join(project_root, "data")
index_path = join(data_folder, "campgrounds_index.csv")
base_url = "https://www.recreation.gov/api/camps/availability/campground/"
browser_base_url = "https://www.recreation.gov/camping/campgrounds/"
request_time_format = "%Y-%m-%dT00:00:00.000Z"
response_time_format = "%Y-%m-%dT00:00:00Z"