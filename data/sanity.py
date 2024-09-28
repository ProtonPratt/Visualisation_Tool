import csv
import json

# load image lang data

image_lang = {}

def extract_langdata():
    # Extract language data from JSON
    global image_lang
    lang_consort = 'consortium_langWiseTextBook.json'
    lang_newdata = 'newdataset_language.csv'

    # load the consortium data
    with open(lang_consort) as f:
        consortium_data = json.load(f)

    # load the new data which is csv
    with open(lang_newdata) as f:
        reader = csv.reader(f)
        new_data = {}
        for row in reader:
            new_data[row[0]] = row[1]

    # # check if the keys are same
    # for key in consortium_data.keys():
    #     if key in new_data.keys():
    #         print(f'Key found in new data: {key}')
    
    image_lang = consortium_data | new_data
    
extract_langdata()

image_name = '0003_ValmeekiRamayanam_Img_600_Org_Page_0073.tif'

def hello():
    print(image_lang)
    
def get_image_lang(image_name):
    return image_lang.get(image_name.split('_')[0], 'Unknown')

hello()
# print(get_image_lang(image_name))
# print(image_lang.get(image_name.split('_')[0], 'Unknown'))

# for i in image_lang.values():
print(set([i for i in image_lang.values()]))
languages = set([i.lower() for i in image_lang.values()])
for i in languages:
    print(i)

# print all keys where value is 'un'
for key, value in image_lang.items():
    if value.lower() == 'un':
        print(key)