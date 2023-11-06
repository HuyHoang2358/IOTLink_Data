import requests
import json
import os
import aspose.threed as a3d

URL = "https://api-app.map4d.vn/map/object/"
SAVE_FOLDER_PATH = "data/"
SAVE_FOLDER_JSON_PATH = SAVE_FOLDER_PATH + "json/"
SAVE_FOLDER_OBJ_PATH =  SAVE_FOLDER_PATH + "obj/"
SAVE_FOLDER_TEXTURE_PATH =  SAVE_FOLDER_PATH + "texture/"
SAVE_FOLDER_GLB_PATH =  SAVE_FOLDER_PATH + "glb/"

DOWNLOADED_IDS_FILE = "log/downloaded_id.txt"
ERROR_IDS_FILE = "log/error_ids.txt"
OBJECT_IDS_FILE = "object_id.txt"
logs = []


# Return unique ids
def processing_list_from_file(file_path):
    list_id = []
    with open(file_path, 'r') as f: 
        lines = f.readlines()
    for line in lines:
        if line[:-1] != "":
            list_id.append(line[:-1])
    # validate unique
    list_id_set = set(list_id)
    unique_list_ids = (list(list_id_set))
    return unique_list_ids

def write_log(log_content, padding = 0):
    global logs
    log_content = " " * padding + log_content
    print(log_content)
    logs.append(log_content)


def init():
    if os.path.exists(SAVE_FOLDER_PATH) == False:
        os.mkdir(SAVE_FOLDER_PATH)
        print(f"Created {SAVE_FOLDER_PATH}")

    if os.path.exists(SAVE_FOLDER_JSON_PATH) == False:
        os.mkdir(SAVE_FOLDER_JSON_PATH)
        print(f"Created {SAVE_FOLDER_JSON_PATH}")
    
    if os.path.exists(SAVE_FOLDER_OBJ_PATH) == False:
        os.mkdir(SAVE_FOLDER_OBJ_PATH)
        print(f"Created {SAVE_FOLDER_OBJ_PATH}")

    if os.path.exists(SAVE_FOLDER_TEXTURE_PATH) == False:
        os.mkdir(SAVE_FOLDER_TEXTURE_PATH)
        print(f"Created {SAVE_FOLDER_TEXTURE_PATH}")
    
    if os.path.exists(SAVE_FOLDER_GLB_PATH) == False:
        os.mkdir(SAVE_FOLDER_GLB_PATH)
        print(f"Created {SAVE_FOLDER_GLB_PATH}")


def get_data_by_id(object_id):
    global downloaded_ids
    global error_ids
    try:
        main_url = URL + object_id
        response = requests.get(main_url)
        with open(SAVE_FOLDER_JSON_PATH + object_id + '.json', 'w') as f:
            json.dump(json.loads(response.text), f, indent=4)

        city_object = json.loads(response.text)["result"]
        model = city_object["model"]
        objUrl = model["objUrl"]
        objImg = model["textureUrl"]

        response = requests.get(objUrl)
        open(SAVE_FOLDER_OBJ_PATH + object_id +".obj", "wb").write(response.content)

        response = requests.get(objImg)
        open(SAVE_FOLDER_TEXTURE_PATH + object_id +".png", "wb").write(response.content)

        # convert obj to glb
        scene = a3d.Scene.from_file(SAVE_FOLDER_OBJ_PATH + object_id +".obj")
        scene.save(SAVE_FOLDER_GLB_PATH + object_id +".glb")

        downloaded_ids.append(object_id)
        write_log(f'{object_id} --- Successfull')

    except Exception as e:
        error_ids.append(object_id)
        write_log(f'{object_id} ---  False')
        print(e)


def get_object_id(object_id_file, downloaded_object_id_file ):
    global downloaded_ids
    write_log(f"Getting object id from {object_id_file} file")

    # read object id from file
    object_ids = processing_list_from_file(object_id_file)
    write_log(f"Total object ids: {len(object_ids)}")
    print(object_ids)

    # check downloaded id 
    downloaded_ids = processing_list_from_file(downloaded_object_id_file)
    write_log(f"Total downloaded ids: {len(object_ids)}")
    write_log(f"Comparing downloaded ids with new ids")

    new_ids = set(object_ids) - set(downloaded_ids)
    write_log(f"Total file will download: {len(new_ids)}")
    return list(new_ids)

def write_list_to_txt_file(file_path, list_arr):
    with open(file_path, 'w') as fp:
        for item in list_arr:
            fp.write("%s\n" % item)


error_ids = processing_list_from_file(ERROR_IDS_FILE)
downloaded_ids = []

def main():
    init()
    OBJECT_ID_FILE = OBJECT_IDS_FILE
    DOWNLOADED_OBJECT_ID_FILE =  DOWNLOADED_IDS_FILE

    object_ids = get_object_id(OBJECT_ID_FILE, DOWNLOADED_OBJECT_ID_FILE)

    write_log(f"Strating download all model by ID --------------------------------")
    write_log(f"----  All data will save in data/ folder") 
    write_log(f"----  With each object ID we will save 3 files - .obj, .json, .png")
    write_log(f"----  .obj save shape model")
    write_log(f"----  .json save all static information of model")
    write_log(f"----  .png save all texture ")
    write_log(f"*****************************Starting*****************************")
    write_log(f"Number of downloading files: {len(object_ids)}")

    for index,id in enumerate(object_ids):
        get_data_by_id(id)

    with open('log/logs.json', 'w') as f:
        json.dump(logs, f)
    write_list_to_txt_file(ERROR_IDS_FILE, error_ids)
    write_list_to_txt_file(DOWNLOADED_IDS_FILE, downloaded_ids)

main()