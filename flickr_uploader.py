from flickrapi import FlickrAPI
from os.path import exists
from xml.etree import ElementTree

def get_authorized_flickr_object_oob(opt):
    flickr = None
    filename = opt.get('client_secret')
    with open(filename) as f:
        keys = json.load(f)
    flickr = FlickrAPI(keys['key'], keys['secret'])
    if not flickr.token_valid(perms='write'):
        # Note: no refresh process.
        flickr.get_request_token(oauth_callback='oob')
        authorize_url = flickr.auth_url(perms='write')
        print('Please connect follwing url to complete authentication:')
        print(authorize_url)
        code = input('Enter verifier code: ').strip()
        flickr.get_access_token(code)
    return flickr

def upload(flickr, filename):
    rsp = flickr.upload(filename=filename)
    ElementTree.dump(rsp)

if __name__ == '__main__':
    from argparse import ArgumentParser
    from os.path import exists
    import json
    import logging
    import flickrapi
    flickrapi.set_log_level(logging.DEBUG)
    parser = ArgumentParser('Script to upload an image to Flickr.')
    parser.add_argument('filename', help='filename of image to upload')
    parser.add_argument('-s', '--client-secret', default='client_secret.json',
            help='specify Client-Secret JSON file, which stores API key and secret. defalt: client_secret.json')
    opt = parser.parse_args()
    flickr = get_authorized_flickr_object_oob(vars(opt))
    upload(flickr, opt.filename)