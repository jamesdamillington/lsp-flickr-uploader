from flickrapi import FlickrAPI

# from os.path import exists
from xml.etree import ElementTree
import csv
import requests  # for image download
import os


def get_authorized_flickr_object_oob(opt):
    flickr = None
    filename = opt.get("client_secret")
    with open(filename) as f:
        keys = json.load(f)
    flickr = FlickrAPI(keys["key"], keys["secret"])
    if not flickr.token_valid(perms="write"):
        # Note: no refresh process.
        flickr.get_request_token(oauth_callback="oob")
        authorize_url = flickr.auth_url(perms="write")
        print("Please connect following url to complete authentication:")
        print(authorize_url)
        code = input("Enter verifier code: ").strip()
        flickr.get_access_token(code)
    return flickr


def get_response_form_name(opt):
    form_name = None
    filename = opt.get("client_secret")
    with open(filename) as f:
        keys = json.load(f)
    form_name = keys["responses"]
    return form_name


def get_album_ids(opt):
    albums_dict = None
    filename = opt.get("client_secret")
    with open(filename) as f:
        keys = json.load(f)
    albums_dict = keys["album_ids"]
    return albums_dict


def YesNoUK(b):
    # convert Yes|No to 'UK'|'non-UK'
    return "UK" if b == "Yes" else "non-UK"


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value

    return None


def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


def download_file_from_google_drive(id, destination):
    # from https://stackoverflow.com/a/39225272
    # this works assuming file is viewable to anyone on the web with link
    # for private image try https://stackoverflow.com/a/38516081
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params={"id": id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {"id": id, "confirm": token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)


def create_tags(tags_ot, uk, tags_le):

    # ## other tags ##
    # create python list of tags
    tags_ot = tags_ot.split(",")

    # strip leading whitespace from any tags
    for i, item in enumerate(tags_ot):
        tags_ot[i] = item.lstrip()

    # put quotes around any tags containing spaces
    for i, item in enumerate(tags_ot):
        if " " in item:
            tags_ot[i] = f'"{item}"'

    # add UK/non-UK tag
    tags_ot.append(YesNoUK(uk))

    # ## lsp tags ##
    # create python list of tags
    tags_le = tags_le.split(",")

    # get short tag from between [ ]
    for i, item in enumerate(tags_le):
        tags_le[i] = item.split("[")[-1].rstrip("]")

    # ## all tags ##
    tags_all = tags_le + tags_ot

    # collapse python comma sep list to space sep for upload
    tags_all = " ".join(tags_all)

    return tags_all


def upload(flickr, rfilename, album_ids):

    # opening the CSV file
    with open(rfilename, mode="r") as file:

        csvFile = csv.reader(file)
        next(file)  # skip column header line
        for lines in csvFile:
            # print(lines)
            name = lines[1]
            # email = lines[2]
            title = lines[3]
            albums = lines[6]
            # tags_le = lines[5]
            # uk = lines[6]
            year = lines[5]
            image_loc = lines[7]
            # tags_ot = lines[9]
            descr_free = lines[10]
            lat = lines[11]
            lon = lines[12]

            print("Title: " + title)

            descr_all = "Credit: ialeUK/" + name + " " + year + "\n\n" + descr_free
            print("Description: " + descr_all)

            print("Albums: " + albums)
            # always split (if only one album it will have trailing comma)
            albums = albums.split(", ")

            # recode album names to album ids
            for a, item in enumerate(albums):
                albums[a] = album_ids[item]

            tags_all = create_tags(lines[8], lines[4], lines[9])
            print("Tags: " + tags_all)

            # ## IMAGE ##
            # if image is to be accessed from GDrive (e.g. vai GForm )
            if "https://drive.google.com/open?" in image_loc:
                image_name = "image_name.jpg"
                # next line from https://stackoverflow.com/a/6169363
                image_id = image_loc.split("=")[-1]
                download_file_from_google_drive(image_id, image_name)
            # else image is to be accessed direct from filename
            else:
                image_name = image_loc

            # ## UPLOAD ##
            rsp = flickr.upload(
                filename=image_name, title=title, description=descr_all, tags=tags_all,
            )

            # ## ADD TO ALBUM(S) ##
            # see https://docs.python.org/3/library/xml.etree.elementtree.html
            photoid = rsp[0].text

            for id in albums:
                flickr.photosets_addPhoto(photoset_id=id, photo_id=photoid)

            # ## ADD LOCATION ##
            if lat.strip():
                if lon.strip():
                    print("Lat:" + lat + " Lon:" + lon)
                    flickr.photos.geo.setLocation(
                        photo_id=photoid, lat=float(lat), lon=float(lon)
                    )

            # ## CLEAN UP ##
            ElementTree.dump(rsp)

            if "https://drive.google.com/open?" in image_loc:
                os.remove(image_name)


if __name__ == "__main__":
    from argparse import ArgumentParser

    # from os.path import exists
    import json
    import logging
    import flickrapi

    flickrapi.set_log_level(logging.DEBUG)
    parser = ArgumentParser(description="Script to upload an image to Flickr.")
    parser.add_argument(
        "-s",
        "--client_secret",
        default="client_secret.json",
        help="specify Client_Secret JSON file, which stores \
                        API key and secret. default: client_secret.json",
    )
    parser.add_argument(
        "-r",
        "--responses_filename",
        default=1,
        help="specify filename of responses spreadsheet. If not specified, \
                    filename will be taken from 'responses' in Client_Secret \
                    JSON",
    )
    opt = parser.parse_args()

    flickr = get_authorized_flickr_object_oob(vars(opt))
    if opt.responses_filename == 1:
        responses_filename = get_response_form_name(vars(opt))
    else:
        responses_filename = opt.responses_filename

    print("\nUsing responses from: " + responses_filename + "\n")

    album_ids = get_album_ids(vars(opt))
    # if opt.filename:
    upload(flickr, responses_filename, album_ids)
