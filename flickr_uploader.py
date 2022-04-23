from flickrapi import FlickrAPI

# from os.path import exists
from xml.etree import ElementTree
import csv
import requests  # for image download


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


def YesNoBin(b):
    # convert Yes|No to 1|0
    return 1 if b == "Yes" else 0


def upload(flickr, rfilename):

    print(rfilename)

    # opening the CSV file
    with open(rfilename, mode="r") as file:
        # reading the CSV file
        csvFile = csv.reader(file)
        next(file)
        # displaying the contents of the CSV file
        for lines in csvFile:
            # print(lines)
            name = lines[1]
            email = lines[2]
            title = lines[3]
            albums = lines[4]
            tags_le = lines[5]
            uk = lines[6]
            year = lines[7]
            image_url = lines[8]
            tags_ot = lines[9]
            description = lines[10]
            lat = lines[11]
            lon = lines[12]

            # split multiple albums if necessary
            if "," in albums:
                albums = albums.split(", ")

            # convert Yes|No to 1|0
            uk = YesNoBin(uk)

            print(name)
            print(email)
            print(title)
            print(albums)
            print(tags_le)
            print(uk)
            print(year)
            print(image_url)
            print(tags_ot)
            print(description)
            print(lat)
            print(lon)

    """
    def b2i(b):
        return 1 if b else 0
    rsp = flickr.upload(filename=opt.get('filename'),
                        is_public=b2i(opt.get('public')),
                        is_family=b2i(opt.get('family')),
                        is_friend=b2i(opt.get('friend')))
    ElementTree.dump(rsp)
    """


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
    # if opt.filename:
    upload(flickr, responses_filename)
