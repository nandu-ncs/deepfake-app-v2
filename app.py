from flask import Flask
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.utils import secure_filename
import os
import shutil

import tensorflow as tf
import dlib
import cv2
import os
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img


app = Flask(__name__)
upload_dir = 'static/uploads'

name = ""
res = []
rr = []
rr2 = []
count = 0
frames = []
faces = []


@app.route('/')
def index():
    global upload_dir
    folder = os.path.join(os.getcwd(), upload_dir)
    try:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    except Exception as e:
        print('Failed to delete.', e)

    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    global name, upload_dir
    if request.method == 'POST':
        folder = os.path.join(os.getcwd(), upload_dir)
        try:
            if os.path.exists(folder):
                shutil.rmtree(folder)
            os.mkdir(folder)
            os.mkdir(folder+"/frames")
            os.mkdir(folder+"/faces")
        except Exception as e:
            print('Failed to delete.', e)

        f = request.files['file']
        filename = secure_filename(f.filename)
        f.save(os.path.join(upload_dir, filename))
        name = filename

        return "True"
    else:
        return "False"


@app.route('/page2')
def page2():
    global name
    print(name)
    return render_template('page2.html', video=name)


@app.route('/pred', methods=['POST'])
def pred():
    if request.method == 'POST':
        global name, res, count, rr, rr2, upload_dir, frames, faces
        gnet = []
        dnet = []

        gnet_pred = []
        dnet_pred = []

        model_google = load_model(os.path.join(
            os.getcwd(), 'models\Googlenet_Model.h5'))
        model_dense = load_model(os.path.join(
            os.getcwd(), 'models\densenet.h5'))

        res = []
        rr = []
        rr2 = []
        print(name)

        file = os.path.join(os.getcwd(), upload_dir, name)

        input_shape = (128, 128, 3)
        pr_data = []
        i1 = 0

        detector = dlib.get_frontal_face_detector()
        cap = cv2.VideoCapture(file)
        frameRate = cap.get(5)
        print(frameRate)
        while cap.isOpened():
            frameId = cap.get(1)
            ret, frame = cap.read()
            print(frameId)
            if ret != True:
                break
            if frameId % ((int(frameRate)+1)*1) == 0:
                face_rects, scores, idx = detector.run(frame, 0)

                imgname = 'frame'+str("{:02d}".format(i1))+'.png'
                dirr1 = os.path.join(
                    upload_dir, "frames", imgname)
                print(dirr1)
                cv2.imwrite(dirr1, frame)
                # frame.save(dirr1)

                for i, d in enumerate(face_rects):

                    x1 = d.left()
                    y1 = d.top()
                    x2 = d.right()
                    y2 = d.bottom()

                    crop_img = frame[y1:y2, x1:x2]
                    imgname = 'face'+str("{:02d}".format(i1))+'.png'
                    dirr1 = os.path.join(
                        upload_dir, "faces", imgname)
                    cv2.imwrite(dirr1, crop_img)

                    data = img_to_array(cv2.resize(
                        crop_img, (128, 128))).flatten() / 255.0
                    data = data.reshape(-1, 128, 128, 3)

                    g = model_google.predict(data)
                    d = model_dense.predict(data)

                    gnet_pred.append(g[0].tolist())
                    dnet_pred.append(d[0].tolist())

                    gnet.append(np.argmax(g, axis=1)[0])
                    dnet.append(np.argmax(d, axis=1)[0])

                    # print(model.predict(data),model.predict_classes(data))
                    # print(model_google.predict(data),np.argmax(model_google.predict(data),axis=1))

                i1 += 1

        gnet_pred_avg = avg(gnet_pred)
        dnet_pred_avg = avg(dnet_pred)

        print(gnet_pred)
        print(dnet_pred)

        print(gnet_pred_avg)
        print(dnet_pred_avg)

        res.append(gnet_pred_avg)
        res.append(dnet_pred_avg)

        print(gnet)
        print(dnet)

        if 0 in gnet:
            zc = gnet.count(0)
        else:
            zc = 0
        if 1 in gnet:
            oc = gnet.count(1)
        else:
            oc = 0

        if zc > oc:
            rr.append(0)
        else:
            rr.append(1)

        if 0 in dnet:
            zc = dnet.count(0)
        else:
            zc = 0
        if 1 in dnet:
            oc = dnet.count(1)
        else:
            oc = 0

        if zc > oc:
            rr.append(0)
        else:
            rr.append(1)

        print(rr)

        rr2.append(np.argmax(gnet_pred_avg))
        rr2.append(np.argmax(dnet_pred_avg))

        print(rr2)

        count = i1

        frames = sorted(os.listdir(os.path.join(upload_dir, "frames")))
        faces = sorted(os.listdir(os.path.join(upload_dir, "faces")))

        return "True"
    else:
        return "False"


@app.route('/result')
def result():
    global res, count, frames, faces
    print(res)
    return render_template('result.html', file=name, res=res, count=count, rr=rr2, rr2=rr, frames=frames, faces=faces)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('err404.html'), 404


def avg(nums):
    result = [sum(x) / len(x) for x in zip(*nums)]
    return result
