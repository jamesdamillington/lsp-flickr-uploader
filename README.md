# Upload images with metadata to Flickr

This code will upload images and associated metadata (title, description, tags, albums, etc) to a flickr account. Intended for use with [ialeUK's flickr](https://www.flickr.com/photos/96878059@N06/), but should be adaptable for use with other accounts. 


## Credit
See the repo licence. This code is developed on base code from [akige](https://github.com/aikige)'s [flickr-uploader](https://github.com/aikige/flickr-uploader) script. Original README for that script is below.

### An sample python script for uploading image to Flickr
[FlickrAPI]:https://github.com/sybrenstuvel/flickrapi/
This is minimal script which utilizes [FlickrAPI] to upload an image to Flickr.

### Preparation

1. Please visit [The Flickr Developer Guide: API](https://www.flickr.com/services/developer/api/), and request API key for this script.
1. Please create `client_secret.json`, which has format like `{ "key": "YOUR_KEY", "secret": "YOUR_SECRET" }` (please replace `YOUR_KEY` and `YOUR_SECRET` to actual value, you got in previous step).
1. Please run this script without arguments, and perform Authentication & Authorization.
    1. This scripts shows URL for authorization process.
    1. Please visit the site and confirm authorization required for this script.
    1. Copy the *Verification Code* shown by Flickr and input it to this script.

### Usage

Please simply run script with an argument which specifies file to be uploaded.

```
python flickr_uploader.py YOUR_IMAGE
```

For other options, please see help by typing `python flickr_uploader.py -h`.

### Note about Behavior

Based on behavior [FlickrAPI], authorization data (credentials) is stored at directory `~/.flickr`. If you have problem in authorization, please try to remove the folder to perform authentication & authorization again.

### References

* [The Flickr Developer Guide: API](https://www.flickr.com/services/developer/api/)
