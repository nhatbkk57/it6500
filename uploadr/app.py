from flask import Flask, request, redirect, url_for, render_template
import os
import json
import glob
from uuid import uuid4
from PIL import Image
from tf_model import *

MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'
print("Loading model")
graph_model = load_model(PATH_TO_CKPT)
print("Import model into memory")

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    """Handle the upload of a file."""
    form = request.form

    # Create a unique "session ID" for this particular batch of uploads.
    upload_key = str(uuid4())

    # Is the upload using Ajax, or a direct POST by the form?
    is_ajax = False
    if form.get("__ajax", None) == "true":
        is_ajax = True

    # Target folder for these uploads.
    target = "uploadr/static/uploads/{}".format(upload_key)
    try:
        os.mkdir(target)
    except:
        if is_ajax:
            return ajax_response(False, "Couldn't create upload directory: {}".format(target))
        else:
            return "Couldn't create upload directory: {}".format(target)

    print "=== Form Data ==="
    for key, value in form.items():
        print key, "=>", value

    results = {}
    files = []
    for upload in request.files.getlist("file"):
        img = Image.open(upload.stream)        
        filename = upload.filename.rsplit("/")[0]
        files.append(filename)
        
        results[filename] = predict_single_label(img,graph_model)
        
        (im_width, im_height) = img.size
        # results[filename]['width'] = im_width
        # results[filename]['height'] = im_height

        destination = "/".join([target, filename])
        print "Accept incoming file:", filename
        print "Save it to:", destination
        img.save(destination)

    print(results)

    return render_template("list_views.html",
        uuid=upload_key,
        files=files,
        labels=results
    )

    # if is_ajax:
    #     return ajax_response(True, upload_key)
    # else:
    #     return view_image_with_label(uuid,results)



@app.route("/files/<uuid>")
def upload_complete(uuid):
    """The location we send them to at the end of the upload."""

    # Get their files.
    root = "uploadr/static/uploads/{}".format(uuid)
    if not os.path.isdir(root):
        return "Error: UUID not found!"

    files = []
    for file in glob.glob("{}/*.*".format(root)):
        fname = file.split(os.sep)[-1]
        files.append(fname)

    return render_template("files.html",
        uuid=uuid,
        files=files,
    )


def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(dict(
        status=status_code,
        msg=msg,
    ))

def view_image_with_label(uuid,labels):
    """The location we send them to at the end of the upload."""

    # Get their files.
    root = "uploadr/static/uploads/{}".format(uuid)
    if not os.path.isdir(root):
        return "Error: UUID not found!"

    files = []
    for file in glob.glob("{}/*.*".format(root)):
        fname = file.split(os.sep)[-1]
        files.append(fname)

    return render_template("list_views.html",
        uuid=uuid,
        files=files,
        labels = labels
    )
