import tarfile
import tensorflow as tf
import zipfile
import six.moves.urllib as urllib
import os


MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
MODEL_FILE = MODEL_NAME + '.tar.gz'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'


# Download model
def download_tensorflow_model():
	if os.path.exists(MODEL_NAME)==False:
		opener = urllib.request.URLopener()
		opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)
		tar_file = tarfile.open(MODEL_FILE)
		for file in tar_file.getmembers():
		  file_name = os.path.basename(file.name)
		  if 'frozen_inference_graph.pb' in file_name:
		    tar_file.extract(file, os.getcwd())

		os.remove(MODEL_FILE)
	print("Model already exists")