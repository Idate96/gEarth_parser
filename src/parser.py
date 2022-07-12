import argparse
from typing import Dict, List
import os


def parser_gearth_data(data_folder, extract_poligons=True) -> Dict[str, Dict[str, List[float]]]:
    """
    Parses xml files output from google Earth
    :param data_folder: folder containing the xml files
    :param extract_poligons: if True, the polygons are extracted from the xml files
    :return: a dictionary containing the names of the images and their polygons
    """
    parsed_data = []
    for file in os.listdir(data_folder):
        if file.endswith(".kml"):
            if extract_poligons:
                polygons = extract_polygons_from_xml(os.path.join(data_folder, file))
                parsed_data.append(polygons)
            else:
                polygons = None
    return parsed_data


def extract_polygons_from_xml(gearth_kml_file) -> Dict[str, List[float]]:
    """
    This function parses the kml output of the gearth tool and extracts the polygons.
    :param gearth_kml_file: the kml file output from the gearth tool
    :return:
    """
    # parse the file with the lxml library
    from lxml import etree
    tree = etree.parse(gearth_kml_file)
    # get the root of the tree
    root = tree.getroot()
    # remove namespace in front of the tags
    for elem in root.getiterator():
        if not elem.tag:
            continue
        if elem.tag[0] == "{":
            elem.tag = elem.tag.split("}", 1)[1]
    # parse the values inside the field "coordinates"
    polygons = {}
    for placemark in root.findall(".//Placemark"):
        name = placemark.find("name").text
        coordinates = placemark.find("Polygon").find("outerBoundaryIs").find("LinearRing").find("coordinates").text
        # filter out \t and \n
        coordinates = coordinates.replace("\n", "").replace("\t", "")
        coordinates = coordinates.split(" ")
        # remove empty strings
        coordinates = [c for c in coordinates if c != ""]
        # each coordinate is a list of 3 values: longitude, latitude and altitude.
        # convert the coordinates to a list of floats
        for coordinate in coordinates:
            coordinate = coordinate.split(",")
            coordinate = [float(c) for c in coordinate]
            if name not in polygons:
                polygons[name] = []
            polygons[name].append(coordinate)
    return polygons


def write_to_csv_file(coordinates, data_folder, file_name):
    with open(data_folder + "/" + file_name, "w") as f:
        for coordinate in coordinates:
            f.write(",".join(str(c) for c in coordinate) + "\n")

if __name__ == '__main__':
    # crate an argument parser
    parser = argparse.ArgumentParser(description='Google Earth Parser')
    # data folder argument
    parser.add_argument('--data_folder', type=str, default='data/', help='data folder')
    parser.add_argument('--extract_poligons', action='store_true', help='extract poligons')
    # parse the arguments
    data = parser_gearth_data(parser.parse_args().data_folder)
    print(data)
    for coordinate_dict in data:
        name = list(coordinate_dict.keys())[0]
        print(name)
        coordinates = coordinate_dict[name]
        write_to_csv_file(coordinates,  parser.parse_args().data_folder , name + ".csv")