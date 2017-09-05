from flask import Flask, request, redirect, url_for, render_template
import os
import json
import glob
from uuid import uuid4
from hashlib import md5 
from PIL import Image
import logging
from datetime import datetime

from tf_model import *
from models import ImageStorage, ImageLabel, Session
from storage import Storage

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'
print("Loading model")
graph_model = load_model(PATH_TO_CKPT)
print("Import model into memory")

app = Flask(__name__)

@app.route("/uploads")
def uploads():
    return render_template("upload.html")
@app.route("/")
def index():
    storage = Storage()
    records = ImageStorage.query.all()
    images = []
    #TEST
    for record in records:
        print record.photo_id
        try:
            obj = storage.get(record.photo_id)
        except:
            print "Oops!  Object not exist"
            continue
        if obj:
            image = {}
            image["photo_id"] = record.photo_id
            image["photo_name"] = record.photo_link
            image["photo_des"] = "Photo Description"
            target = "uploadr/static/uploads/{}".format(image["photo_id"])
            try:
                with open(target, 'w') as temp:
                    temp.write(obj[1])
                images.append(image)
            except:
                print "Oops!  Store error.  Try again..."
                continue
    return render_template("index.html",images=images)
@app.route("/storage")
def test_storage():
    storage = Storage()
    return json.dumps(storage.list_object())

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

    results = {}
    files = []
    # storage = Storage()
    # for upload in request.files.getlist("file"):
    #     filename = upload.filename.rsplit("/")[0]
    #     storage.put(filename,upload.stream)
    #     files.append(filename)

    for upload in request.files.getlist("file"):
        print upload.content_type
        img = Image.open(upload.stream)        
        filename = upload.filename.rsplit("/")[0]
        results[filename] = predict_single_label(img,graph_model)
        (im_width, im_height) = img.size
        photo_id = md5(filename+ str(datetime.now())).hexdigest()
        image_metadata = ImageStorage(photo_id=photo_id,
            photo_link=filename,
            created_at=datetime.now(),
            user_id=1,
            meta_labels="",
            width=im_width,
            height=im_height)
        Session.add(image_metadata)
        for item in results[filename]:
            score = float(item['score'])
            class_name = item['class']
            image_label = ImageLabel(photo_id=photo_id,
                label_id = 1,
                label_text = class_name,
                bound_bnx ="",
                confidence=score)
            Session.add(image_label)

        #Save to local
        destination = "/".join([target, filename])
        print "Accept incoming file:", filename
        print "Save it to:", destination
        img.save(destination)

        #Put to storage
        storage = Storage()
        print "Storing to cloud storage - container", storage.container_name
        with open(destination, 'r') as temp_img:
            storage.conn.put_object(
                'guest',
                photo_id,
                contents=temp_img,
                content_type=upload.content_type
            )
        print "Done"

    Session.commit()
        # Add to PostgresSQL
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

@app.route("/image/<file_name>")
def image(file_name):
    storage = Storage()
    obj = storage.get(file_name)
    files = []
    img = {}
    if obj:
        img["photo_id"] = file_name
        img["photo_name"] = "Photo Name"
        img["photo_des"] = "Photo Description"
        img["photo_source"] = 'https://objectstorage-ui.ng.bluemix.net/v2/service_instances/2d244042-a005-427f-aa2d-e6234a826ca1/region/dallas/container/guest/'+file_name
        files.append(img)
        return render_template("object.html",
        files=files,
    )
