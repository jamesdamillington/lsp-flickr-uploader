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

    print(rfilename)

    # opening the CSV file
    with open(rfilename, mode="r") as file:

        csvFile = csv.reader(file)
        next(file)  # skip column headers
        for lines in csvFile:
            # print(lines)
            name = lines[1]
            # email = lines[2]
            title = lines[3]
            albums = lines[4]
            # tags_le = lines[5]
            # uk = lines[6]
            year = lines[7]
            image_url = lines[8]
            # tags_ot = lines[9]
            descr_free = lines[10]
            lat = lines[11]
            lon = lines[12]

            descr_credit = "Credit: ialeUK/" + name + " " + year

            # always split (if only one album it will have trailing comma)
            albums = albums.split(", ")

            # recode album names to album ids
            for a, item in enumerate(albums):
                albums[a] = album_ids[item]

            tags_all = create_tags(lines[9], lines[6], lines[5])

            # ## IMAGE ##
            # next line from https://stackoverflow.com/a/6169363
            image_id = image_url.split("=")[-1]
            download_file_from_google_drive(image_id, "image_name.jpg")

            print("Title: " + title)
            print("Description: " + descr_credit)
            print("Albums: " + albums)
            # print(tags_le)
            # print(uk)
            # print(image_url)
            print("Tags: " + tags_all)
            # print(descr_free)
            # print(lat)
            # print(lon)

            # ## UPLOAD ##
            rsp = flickr.upload(
                filename="image_name.jpg",
                title=title,
                description=descr_credit,
                tags=tags_all,
            )

            # ## ADD TO ALBUM(S) ##
            # see https://docs.python.org/3/library/xml.etree.elementtree.html
            photoid = rsp[0].text
            print("PhotoID: " + photoid)

            for id in albums:
                flickr.photosets_addPhoto(photoset_id=id, photo_id=photoid)

            # ## CLEAN UP ##
            ElementTree.dump(rsp)

            os.remove("image_name.jpg")


if __name__ == "__main__":
    from argparse import ArgumentParser

    # from os.path import exists
    import json
    import logging
    import flickrapi

    flickrapi.set_log_level(logging.DEBUG)
    parser = ArgumentParser(description="Script to upload an image to Flickr.")
    """
    parser.add_argument('filename', nargs='?', default=None,
                        help='filename of image to upload')
    parser.add_argument('-p', '--public', action='store_true',
                        help='make uploaded image public')
    parser.add_argument('-fa', '--family', action='store_true',
                        help='make uploaded image visible to your familgy')
    parser.add_argument('-fr', '--friend', action='store_true',
                        help='make uploaded image visible to your friend')
    """
    parser.add_argument(
        "-s",
        "--client-secret",
        default="client_secret.json",
        help="specify Client-Secret JSON file, which stores \
                        API key and secret. defalt: client_secret.json",
    )
    opt = parser.parse_args()
    flickr = get_authorized_flickr_object_oob(vars(opt))
    responses_filename = get_response_form_name(vars(opt))
    album_ids = get_album_ids(vars(opt))
    # if opt.filename:
    upload(flickr, responses_filename, album_ids)
