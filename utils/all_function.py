import os,json
from termcolor import colored

def clear_data(destination_path:str):
    from shutil import rmtree
    rmtree(os.path.join(destination_path + '/images'))
    rmtree(os.path.join(destination_path + '/json'))

def crop_image(link : str,save_path : str,destination_path : str):
    from warnings import filterwarnings
    download_status = False
    try:
        filterwarnings("ignore",category = RuntimeWarning)
        import cv2,requests
        from copy import copy
        from PIL import Image
        while not download_status:
            status = requests.get(link, stream=True)
            img = Image.open(status.raw)
            img.save(save_path,quality=95,subsample=0)
            status = str(status)
            if status == '<Response [200]>':
                download_status = True
    except:
        return False
    return download_status

def get_polylines(file_name: str):
    from warnings import filterwarnings
    filterwarnings("ignore", category=RuntimeWarning)
    try:
        import numpy as np
        import cv2
        img = cv2.imread(file_name, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ret, thresh = cv2.threshold(gray, 127, 255, 0)

        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        areas = dict()
        segmentation = dict()
        area_indexes = dict()
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            areas[w * h] = img[y:y + h, x:x + w]
            area_indexes[w * h] = ((x, y), (x + w, y + h))
            segmentation[w * h] = cnt

        second_highest = [i for i in sorted(areas.keys())][-1]

        contours = [segmentation[second_highest]]

        polygon = list()
        for cnt in contours:

            approx = cv2.approxPolyDP(cnt, 0.009 * cv2.arcLength(cnt, True), True)
            n = approx.ravel()
            i = 0

            for j in n:
                if (i % 2 == 0):
                    x = n[i]
                    y = n[i + 1]

                    if (i == 0):
                        pass
                    else:
                        polygon.append((x, y))
                i = i + 1
        return np.array(polygon)
    except:
        return np.array([])

def extract_poly_lines(mask: str, data_id):
    from warnings import filterwarnings
    filterwarnings("ignore", category=RuntimeWarning)
    import cv2, os, requests
    import numpy as np
    from PIL import Image
    try:
        status = requests.get(mask, stream=True)
        img = Image.open(status.raw)
        img.save('temp_mask' + str(data_id) + '.png', quality=95, subsample=0)
        list_arrays = get_polylines('temp_mask' + str(data_id) + '.png')
        os.remove('temp_mask' + str(data_id) + '.png')
        return list_arrays
    except:
        return np.array([])


def pre_process(start_index,data,destination_path,json_path):
    from warnings import filterwarnings
    filterwarnings("ignore",category = RuntimeWarning)
    import cv2,json,os
    for file_name,files in enumerate(data):
        link = files['Labeled Data']
        path = os.path.join(destination_path, str(file_name + start_index) + '.jpg')
        image = crop_image(link=link, save_path=os.path.normpath(path), destination_path=destination_path)
        if image == True:
            data_number = 0
            annotations = list()
            for annotation in files['Label']['objects']:
                except_ = True
                count = 0
                while except_:
                    try:
                        list_arrays = extract_poly_lines(annotation["instanceURI"],
                                                         file_name + start_index + data_number)
                        left, top, width, height, = cv2.boundingRect(list_arrays)
                        annotation["bbox"] = {"top": abs(left),
                                              "left": abs(top),
                                              "height": height,
                                              "width": width}
                        if annotation.get("polygon") is None:
                            annotation["polygon"] = [{"x": x, "y": y} for x, y in
                                                     list_arrays.tolist()]
                            annotation["polygon"].append({"x": abs(left), "y": abs(top)})
                        else:
                            annotation["polygon"] = [{"x": x, "y": y} for x, y in
                                                     [list(x.values()) for x in annotation['polygon']]]
                        except_ = False
                        annotations.append(annotation)
                    except:
                        count = count + 1
                        if count == 20:
                            except_ = False
                data_number = data_number + 1
            files["Label"]["objects"] = annotations
        else:
            pass
        files["Local Storage Path"] = os.path.normpath(os.path.join('images', str(file_name + start_index) + '.jpg'))
    json_object = json.dumps(data, indent = 4)
    with open(os.path.normpath(os.path.join(json_path,str(start_index)+".json")), "w") as outfile:
        outfile.write(json_object)

def combine_all_data(json_path):
    from warnings import filterwarnings
    filterwarnings("ignore",category = RuntimeWarning)
    final_data = list()
    for i in os.listdir(json_path):
        json_file = open(os.path.join(json_path,i))
        data = json.load(json_file)
        final_data.extend(data)
        json_file.close()

    for i in os.listdir(json_path):
        os.remove(os.path.join(json_path,i))

    json_object = json.dumps(final_data, indent=4)
    with open(os.path.join(json_path,"Final.json"), "w+") as outfile:
        outfile.write(json_object)

def process_json(json_path,count):
    import time
    from tqdm import tqdm
    try:
        with tqdm(total=count,colour="green") as pbar:
            total_ = 0
            old_last = 0
            while( True ):
                time.sleep(2)
                last = len(os.listdir(json_path))
                if old_last == last:
                    pass
                else:
                    pbar.update(abs(last-total_))
                    old_last = last
                    total_ = last
                if len(os.listdir(json_path)) == count:
                    break
        combine_all_data(json_path=json_path)
        os.kill(os.getpid(), 9)
    except KeyboardInterrupt:
        os.kill(os.getpid(),9)

def process_images(image_path,count):
    import time
    from tqdm import tqdm
    try:
        with tqdm(total=count, colour="blue") as pbar:
            total_ = 0
            old_last = 0
            while( True ):
                #time.sleep(2)
                last = len(os.listdir(image_path))
                if old_last == last:
                    pass
                else:
                    pbar.update(abs(last - total_))
                    old_last = last
                    total_ = last
                if len(os.listdir(image_path)) == count:
                    break
    except KeyboardInterrupt:
        os.kill(os.getpid(),9)

