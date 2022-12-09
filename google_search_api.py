import requests, lxml, re, json, urllib.request
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import os, sys, time
from alive_progress import alive_bar

def get_original_images():

    google_images = []

    all_script_tags = soup.select("script")

    # https://regex101.com/r/48UZhY/4
    matched_images_data = "".join(
        re.findall(r"AF_initDataCallback\(([^<]+)\);", str(all_script_tags)))

    # https://kodlogs.com/34776/json-decoder-jsondecodeerror-expecting-property-name-enclosed-in-double-quotes
    # if you try to json.loads() without json.dumps() it will throw an error:
    # "Expecting property name enclosed in double quotes"
    matched_images_data_fix = json.dumps(matched_images_data)
    matched_images_data_json = json.loads(matched_images_data_fix)

    # https://regex101.com/r/VPz7f2/1
    matched_google_image_data = re.findall(
        r'\"b-GRID_STATE0\"(.*)sideChannel:\s?{}}', matched_images_data_json)

    # https://regex101.com/r/NnRg27/1
    matched_google_images_thumbnails = ", ".join(
        re.findall(
            r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]',
            str(matched_google_image_data))).split(", ")

    thumbnails = [
        bytes(bytes(thumbnail, "ascii").decode("unicode-escape"),
              "ascii").decode("unicode-escape")
        for thumbnail in matched_google_images_thumbnails
    ]

    # removing previously matched thumbnails for easier full resolution image matches.
    removed_matched_google_images_thumbnails = re.sub(
        r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]',
        "", str(matched_google_image_data))

    # https://regex101.com/r/fXjfb1/4
    # https://stackoverflow.com/a/19821774/15164646
    matched_google_full_resolution_images = re.findall(
        r"(?:'|,),\[\"(https:|http.*?)\",\d+,\d+\]",
        removed_matched_google_images_thumbnails)

    full_res_images = [
        bytes(bytes(img, "ascii").decode("unicode-escape"),
              "ascii").decode("unicode-escape")
        for img in matched_google_full_resolution_images
    ]

    for index, (metadata, thumbnail, original) in enumerate(zip(
            soup.select(".isv-r.PNCib.MSM1fd.BUooTd"), thumbnails,
            full_res_images),
                                                            start=1):
        # google_images.append({
        #     "title":
        #     metadata.select_one(".VFACy.kGQAp.sMi44c.lNHeqe.WGvvNb")["title"],
        #     "link":
        #     metadata.select_one(".VFACy.kGQAp.sMi44c.lNHeqe.WGvvNb")["href"],
        #     "source":
        #     metadata.select_one(".fxgdke").text,
        #     "thumbnail":
        #     thumbnail,
        #     "original":
        #     original
        # })

        # This code uses for more link
        # if "amazon" in original or "wiley" in original:
        #     google_images.append(original)
        if "amazon" in original:
            google_images.append(original)
        if len(google_images) == 10:
            break

    return google_images

def compute():
    for i in range(1000):
        ... # process items as usual.
        yield  # insert this :)
# ----------------------------------------------------------------------------------
# Load titles
data = pd.read_csv("title.csv").reset_index(drop=True)

# Convert titles to list
titles = list(data.title)


# Create new folder
path = './new_book_images'
isExist = os.path.exists(path)
if not isExist:
   # Create a new directory because it does not exist
   os.makedirs(path)

# Change directory
os.chdir(path)

with alive_bar(1000) as bar:
    for i in compute():
        pass

    for index, title in enumerate(titles):
        # # Progress bar
        # time.sleep(0.1)  # do real work here
        # # update the bar
        # sys.stdout.write("-")
        # sys.stdout.flush()

        # For test
        # if index == 10:
        #     break
        headers = {
            "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36"
        }

        params = {
            "q": f"Amazon {title} book", # search query
            "tbm": "isch",  # image results
            "hl": "en",  # language of the search
            "gl": "us",  # country where search comes from
            "ijn": "0"  # page number
        }

        html = requests.get("https://www.google.com/search",
                            params=params,
                            headers=headers)
        soup = BeautifulSoup(html.text, "lxml")

        # Handle title to image name
        title = title.lower().replace(' ', '-').replace('/','')\
                        .replace('(','').replace(')','').replace(':','')\
                        .replace('+','').replace("&", 'and').replace("#", "")\
                        .replace('"', '').replace('â', '')
        for char in title:
            if not char.isalnum():
                title = title.replace(char, '_')
        print(title)

        # Crawl image
        try:
            image = get_original_images()[0]
        except:
            print(title)
            continue

        img_data = requests.get(image).content

        # Save image
        with open(f'{title}.jpg', 'wb') as handler:
            handler.write(img_data)

        bar()
