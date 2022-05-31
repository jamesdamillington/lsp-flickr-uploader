# Upload images with metadata to Flickr
Python script to upload images and associated metadata (title, description, tags, albums, etc.) to a Flickr account. It works for [ialeUK's Flickr account](https://www.flickr.com/images/96878059@N06/) - the landscape ecology image library - but should be adaptable for use with other accounts.

## Credits
See the [repo licence](LICENSE). This script builds on code from [akige](https://github.com/aikige)'s [flickr-uploader](https://github.com/aikige/flickr-uploader) script. The script utilizes the [FlickrAPI](https://github.com/sybrenstuvel/flickrapi/) (and see [requirements.txt](requirements.txt)). See comments in code for other minor acknowledgements.

## Preparation
### Flickr Authorisation
1. Visit [The Flickr Developer Guide: API](https://www.flickr.com/services/developer/api/), and request your API key and secret.
2. Create a client `.json` file (default filename `client_secret.json`) with the following name/value pairs:
    1. `"key": "YOUR_KEY"` - replace `YOUR_KEY` with your API key from step 1.  
    2. `"secret": "YOUR_SECRET"` - replace  `YOUR_SECRET` with your secret value from step 1.
3. Run the python script without arguments, and perform Authentication & Authorization.
    1. This scripts shows URL for authorization process.
    2. Visit the site and confirm authorization required for this script.
    3. Copy the *Verification Code* shown by Flickr and input it to the code.

### Metadata
1. Add the following to your client `.json` file:
    1. `"album_ids":{"ALBUM_1": 111111,"ALBUM_2": 222222}` - replace `ALBUM_1`, `ALBUM_2` etc. with the names of albums corresponding to the corresponding [photoset](https://www.flickr.com/help/forum/en-us/72157675237678471/) numbers (replace  `111111` and `222222` with your photoset numbers)
    2. `"responses": "YOUR_FILE.csv"` - (optional) provide the name of the .`csv` file containing the metadata for the images to be uploaded (this is not needed if the filename is provided as an argument with `-f` tag when the script is run - see [Use section](#Use) below)
1. Create a `.csv` (comma separated values) file with the following columns (with headers on first line):
    1. _Timestamp or imageID_ [numeric] - this column is not read but must exist
    2. _Name_ [text] - the name of the author of the image (will appear in the credit for the image)
    3. _Email Address_ [text] - email address of the author (this column is not read but must exist)
    4. _Image Title_ [text] - image title
    5. _UK_ [text] - must be 'Yes' or 'No' to indicate if the image was taken in the UK
    6. _Image Year_ [numeric] - four-digit year in which the image was taken (e.g. 2022)
    7. _Album Names_ [text] - a comma separated list of Album names (already existing in the Flickr account and which match those provided in the client `.json` file) to which the image should belong (can be a single Album name)
    8. _Image Loc_ [text] - local file name or URL of the image to be uploaded to Flickr (currently URLs must be for images stored in a publicly accessible Google Drive folder)
    9. _Tags (General)_ [text] - a comma separated list of tags (descriptive keywords)
    10. _Tags (LE)_ [text] - a comma separated list of tags selected from the landscape ecology tags ([listed below](#Landscape-Ecology-Tags))
    11. _Description_ [text] - a short description to accompany the image
    12. _Latitude_ [numeric] - latitude of the location shown in the image (or where image was taken) provided in decimal degrees (value between 90 and -90)
    13. _Longitude_ [numeric] - latitude of the location shown in the image (or where image was taken) provided in decimal degrees (value between 180 and -180)

Values are not required for all columns for an given image, but a value for _Image Loc_ is required and ideally all images will have information for _Name_, _Image_, _UK_, and _Image Year_ at least. Even if no values are not provided for a column it must exist, and columns must be in the order listed above. The `.csv` file can be created by hand or as the output for a form.

#### Landscape Ecology Tags
The following are valid values for _Tags (LE)_:
- Pattern–Process–Scale relationships of landscapes [Lsp-Pat-Proc]
- Landscape Connectivity and Fragmentation [Lsp-Con-Frag]
- Land Use and Land Cover Change [LUCC]
- Landscape History and Legacy Effects [Lsp-History]
- Landscape and Climate Change Interactions [Lsp-ClimateChg]
- Ecosystem Services in Changing Landscapes [Lsp-ES],
- Green Infrastructure [Lsp-GI]
- Planning and Architecture [Lsp-Plan-Arch]
- Management and Conservation [Lsp-Mgmnt-Cons]
- Cultural Landscapes [Lsp-Cultural]
- Invasives, Pests & Diseases [Lsp-Inv-Pest]

These are derived from [Young et al. (2021)](https://doi.org/10.1007/s10980-019-00945-1).

## Use
To run the script from the command line using the default settings, use:
```
python lsp-flickr-uploader.py
```
This will use information in `client_secret.json` and requires that an appropriate value is provided for the `"responses":` key.

To run when no value is provided for the `"responses":` key, use
```
python lsp-flickr-uploader.py -r "YOUR_FILE.csv"
```
where `"YOUR_FILE.csv"` is the path/name of the `.csv` containing your image information.

For other options, see help by running
```
python lsp-flickr-uploader.py -h
```

### Note about Behaviour
Based on [FlickrAPI](https://github.com/sybrenstuvel/flickrapi/), authorization data (credentials) is stored in directory `~/.flickr`. If you have problems with authorization, try removing the folder and perform authentication & authorization again.
