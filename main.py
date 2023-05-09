import argparse
import os,json
from warnings import filterwarnings
from utils.Functions import Convert_Json_to_Yolo

def main():
    filterwarnings("ignore")
    msg = """Please give input as """

    # Initialize parser
    parser = argparse.ArgumentParser(description = msg)
    parser.add_argument("-f", "--folder_path_to_store", help = "Please give Folder path in string format where you want to download",required=True)
    parser.add_argument("-j", "--json_file", help = "please give location path in string format of LABEL JSON FILE",required=True)
    parser.add_argument("-i", "--images_file", help="please give location path in string where all the images are located",required=True)
    parser.add_argument("-s", "--use_segments",help="please give input Boolean Value 0 or 1 to use segementations", required=True)
    args = parser.parse_args()
    file_path,main_json,images_file = None,None,None
    if args.folder_path_to_store:
        file_path = os.path.normpath(args.folder_path_to_store)
        print("Given Folder path is {}".format(file_path))

    if args.json_file:
        main_json = os.path.normpath(args.json_file)
        print("File given is {}".format(main_json))

    if args.use_segments:
        use_segments = bool(int(args.use_segments))
        print("Use segments = {}".format(use_segments))

    if args.images_file:
        images_file = os.path.normpath(args.images_file)

    if file_path==None or main_json==None or images_file==None :
        print('Please check the arguments using "python main.py -h"')
        return

    try:
        Convert_Json_to_Yolo(Folder_path_to_store_file=file_path,JSON_File=main_json,images_file=images_file,file=main_json,use_segments=use_segments)
    except Exception as e:
        print(e)

        os.kill(os.getpid(),9)

if __name__ == '__main__':
	main()

