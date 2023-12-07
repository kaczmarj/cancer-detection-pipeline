from __future__ import annotations

import sys
import json
from pathlib import Path
import subprocess
import os
import paquo
from natsort import natsorted #add in dependencies?
os.environ['PAQUO_QUPATH_DIR'] = '/home/sggat/QuPath'

def add_image_and_geojson(
    qupath_proj: QuPathProject, *, image_path: Path | str, geojson_path: Path | str
) -> None:
    with open(geojson_path) as f:
        # FIXME: check that a 'features' key is present and raise a useful error if not
        geojson_features = json.load(f)["features"]

    entry = qupath_proj.add_image(image_path)
    # FIXME: test that the 'load_geojson' function exists. If not, raise a useful error
    entry.hierarchy.load_geojson(geojson_features)  # type: ignore


# Store a list of matched slides and geojson files. Linking the slides and geojson in
# this way prevents a potential mismatch by simply listing directories and relying on
# the order to be the same.


def make_qupath_project(wsi_dir, results_dir):

    try:
        from paquo.projects import QuPathProject
    except Exception as e:
        print(
'''QuPath is required to use this functionality but it cannot be found. 
If QuPath is installed, please use define the environment variable 
PAQUO_QUPATH_DIR with the location of the QuPath installation. 
If QuPath is not installed, please install it from https://qupath.github.io/.''')
        sys.exit(1)

    print("Found QuPath successfully!")
    QUPATH_PROJECT_DIRECTORY = "QuPathProject"

    csv_files = list((results_dir/"model-outputs-csv").glob("*.csv"))
    slides_and_geojsons = []

    for csv_file in csv_files:
        file_name = csv_file.stem

        json_file = results_dir/"model-outputs-geojson"/ (file_name + ".json")
        image_file = wsi_dir/(file_name + ".svs")

        if json_file.exists() and image_file.exists():
            matching_pair = (image_file, json_file)
            slides_and_geojsons.append(matching_pair)
        else:
            print(f"Skipping CSV: {csv_file.name} (No corresponding JSON)")

    # csv_list = natsorted([str(file) for file in wsi_dir.iterdir() if file.is_file()])
    # json_list = natsorted([str(file) for file in Path(f"{results_dir}/model-outputs-geojson").iterdir() if file.is_file()])

    # slides_and_geojsons = [
    #     (csv, json) for csv, json in zip(csv_list, json_list)
    # ]

    print(slides_and_geojsons)

    with QuPathProject(QUPATH_PROJECT_DIRECTORY, mode="w") as qp:
        for image_path, geojson_path in slides_and_geojsons:
            try:
                add_image_and_geojson(qp, image_path=image_path, geojson_path=geojson_path)
            except Exception as e:
                print(f"Failed to add image/geojson with error:: {e}")
    print("Successfully created QuPath Project!")