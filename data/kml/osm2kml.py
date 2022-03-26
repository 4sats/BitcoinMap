#!/usr/bin/env python
# -*- coding: utf8

# osm2kml
# Converts OSM file to KML according to parameters given.
# Usage: osm2kml [input_filename.osm] [sort/folder_tag] [name_tag] [description_tags].
# Default for last three parameters: None, name, description.
# Empty paramters ("") permitted beyond filename.


import sys
from xml.etree import ElementTree as ET


version = "0.1.0"


# Output message

def message (line):

	sys.stdout.write (line)
	sys.stdout.flush()


# Add kml structure (document, folder, placemark, point, name etc)

def add_kml_object (parent, name, value):

	kml_object = ET.Element(name)
	if value:
		kml_object.text = value
	parent.append(kml_object)
	return kml_object


# Add kml placemark

def add_kml_placemark (parent, latitude, longitude, name, description):

	kml_placemark = add_kml_object(parent, "Placemark", "")
	kml_point = add_kml_object(kml_placemark, "Point", "")
	add_kml_object(kml_point, "coordinates", "%s,%s" % (longitude, latitude))
	add_kml_object(kml_placemark, "name", name)
	add_kml_object(kml_placemark, "description", "<br>".join(description))
	return kml_placemark



# Main program

if __name__ == '__main__':

	message ("\nGenerate KML file from OSM\n")

	# Read parameters
	
	if len(sys.argv) > 1:
		filename = sys.argv[1].lower()
	else:
		message ("Input filename (.osm) missing\n")
		sys.exit()

	folder_tag = ""
	name_tag = "name"
	description_tags = ["description"]

	if len(sys.argv) > 2:
		folder_tag = sys.argv[2]

		if len(sys.argv) > 3:
			name_tag = sys.argv[3]

			if len(sys.argv) > 4:
				description_tags = sys.argv[4:]

	message ("  OSM file       : %s\n" % filename)
	message ("  Folder tag     : %s\n" % folder_tag)
	message ("  Name tag       : %s\n" % name_tag)
	message ("  Description tag: %s\n" % ", ".join(description_tags))


	# Load OSM file

	tree = ET.parse(filename)
	root = tree.getroot()

	folders = []
	places = []

	for node in root.iter('node'):
		place = {}
		place['latitude'] = node.get('lat')
		place['longitude'] = node.get('lon')
		place['folder'] = ""
		place['name'] = ""
		place['description'] = []

		for tag in node.iter('tag'):
			key = tag.get('k')
			value = tag.get('v')

			if key == folder_tag:
				place['folder'] = value
				if value not in folders:
					folders.append(value)

			if key == name_tag:
				place['name'] = value

			if key in description_tags:
				if len(description_tags) > 1:
					if key.lower() == "website":
						value = '<a href="'+value+'" target="_blank">'+value+'</a>'
					elif key.lower() == "phone":
						value = '<a href="tel:'+value+'">'+value+'</a>'
					elif key.lower() == "email":
						value = '<a href="mailto:'+value+'">'+value+'</a>'
					place['description'].append(key.lower() + ": " + value)
				else:
					place['description'].append(value)

		places.append(place)

	message ("\nLoaded %i nodes\n" % len(places))
	message ("Found %i folders: %s\n" % (len(folders), ", ".join(folders)))


	# Output KML file

	kml_root = ET.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
	kml_document = add_kml_object(kml_root, "Document", "")

	if not folders:
		folders = [""]

	for folder in folders:
		if folder:
			kml_folder = add_kml_object(kml_document, "Folder", "")
			add_kml_object(kml_folder, "name", folder)
		else:
			kml_folder = kml_document

		for place in places:
			if place['folder'] == folder:
				add_kml_placemark (kml_folder, place['latitude'], place['longitude'], place['name'], place['description'])

	filename = filename.replace(".osm", ".kml")
	message ("Saving KML to file '%s'\n" % filename)

	kml_tree = ET.ElementTree(kml_root)
	kml_tree.write(filename, encoding='utf-8', method='xml', xml_declaration=True)

	message ("\n")


