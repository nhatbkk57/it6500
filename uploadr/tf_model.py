#Load a (frozen) Tensorflow model into memory.
import os

import tensorflow as tf
import numpy as np

from utils import label_map_util
from utils import visualization_utils as vis_util



# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('data', 'mscoco_label_map.pbtxt')

NUM_CLASSES = 90

label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)


# helper
def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)

def load_model(PATH_TO_CKPT):
	detection_graph = tf.Graph()
	with detection_graph.as_default():
	  od_graph_def = tf.GraphDef()
	  with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
	    serialized_graph = fid.read()
	    od_graph_def.ParseFromString(serialized_graph)
	    tf.import_graph_def(od_graph_def, name='')
	return detection_graph

def predict_single_label(image,detection_graph):
	with detection_graph.as_default():
		with tf.Session(graph=detection_graph) as sess:
			# image = Image.open(image_path)
			# the array based representation of the image will be used later in order to prepare the
			# result image with boxes and labels on it.
			image_np = load_image_into_numpy_array(image)
			# Expand dimensions since the model expects images to have shape: [1, None, None, 3]
			image_np_expanded = np.expand_dims(image_np, axis=0)
			image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
			# Each box represents a part of the image where a particular object was detected.
			boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
			# Each score represent how level of confidence for each of the objects.
			# Score is shown on the result image, together with the class label.
			scores = detection_graph.get_tensor_by_name('detection_scores:0')
			classes = detection_graph.get_tensor_by_name('detection_classes:0')
			num_detections = detection_graph.get_tensor_by_name('num_detections:0')
			# Actual detection.
			(boxes, scores, classes, num_detections) = sess.run(
			  [boxes, scores, classes, num_detections],
			  feed_dict={image_tensor: image_np_expanded})

			# return np.squeeze(boxes), np.squeeze(scores),\
			# 		np.squeeze(classes),np.squeeze(num_detections)
			squeeze_scores = np.squeeze(scores)
			squeeze_boxes = np.squeeze(boxes)
			squeeze_classes = np.squeeze(classes)
			
			max_boxes_to_draw = 20
			min_score_thresh = 0.5

			results = []
			for i in range(min(max_boxes_to_draw, squeeze_boxes.shape[0])):
				detection = {}
				if squeeze_scores[i] > min_score_thresh:
					detection['class'] = category_index[int(squeeze_classes[i])]['name']
					detection['score'] = squeeze_scores[i]
					# detection['box'] = squeeze_boxes[i]
					results.append(detection)
			return results
