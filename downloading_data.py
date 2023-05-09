import argparse
import os,json
from warnings import filterwarnings
from utils.all_function import pre_process,combine_all_data,process_images,process_json
import threading
import logging
from colorama import Fore
from math import ceil
from tqdm import tqdm
import time

def main():
	try:
		filterwarnings("ignore")
		msg = """Please give input as """

		# Initialize parser
		parser = argparse.ArgumentParser(description = msg)
		parser.add_argument("-f", "--folder_path", help = "Please give Folder path in string format where you want to download",required=True)
		parser.add_argument("-j", "--json_path", help = "please give location path in string format of LABEL JSON FILE",required=True)
		args = parser.parse_args()
		file_path,main_json = None,None
		if args.folder_path:
			file_path = os.path.normpath(args.folder_path)
			print("Given Folder path is {}".format(file_path))
			image_path = os.path.join(file_path,'images')
			json_path = os.path.join(file_path,'json')

			try:
				os.makedirs(image_path)
			except:
				pass

			try:
				os.makedirs(json_path)
			except:
				pass

			print("Images Downloading in {}".format(image_path))
			print("Creating Json in {}".format(json_path))
		if args.json_path:
			main_json = format(os.path.normpath(args.json_path))
			print("File given is {}".format(main_json))
			json_file = open(main_json)
			data = json.load(json_file)
			json_file.close()

		if file_path==None or main_json==None:
			print('Please check the arguments using "python downloading_data.py -h"')
			return

		final_data = list()
		count = 0
		for i in data:
			if len(i['Label']['objects']) == 0:
				count = count + 1
			else:
				final_data.append(i)
		st = time.time()
		data = final_data
		print("There are {} images to download ".format(len(data)))
		print(Fore.RED + "we are creating {} threads to download all files using threads".format(ceil(len(data)//100)))
		print(Fore.RED + 'Please Donot Use your system for a while')
		print(file_path, main_json)
		count = 0
		threads_list = list()
		for i in tqdm(range(0, len(data), 100),colour="red"):
			t = threading.Thread(target=pre_process, args=(i, data[i:100 + i],image_path,json_path))
			threads_list.append(t)
			count = count + 1
		try:
		    for i in threads_list:
		        logging.info(f"Created {i} ")
		    for i in threads_list:
		        i.start()
		    for i in threads_list:
		        logging.info(f"Started {i} ")
		    for i in threads_list:
		        i.join()
		    for i in threads_list:
		        logging.info(f"Completed {i} ")
		    elapsed_time = time.time() - st
		    combine_all_data(json_path)
		    os.kill(os.getpid(),9)		
		except KeyboardInterrupt:
			os.kill(os.getpid(),9)
	except KeyboardInterrupt:
		os.kill(os.getpid(), 9)

if __name__ == '__main__':
	main()

