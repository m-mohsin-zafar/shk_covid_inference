import os
from flask import Flask, render_template, request
from inference import Inference
app = Flask(__name__)

infer = Inference()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        print(request.files)
        if 'file' not in request.files:
            print('File not Uploaded..!')
            return
        file = request.files['file']
        img = file.read()
        pred_class, pred_cls_name, conf_scr = infer.get_prediction(image_bytes=img)
        return render_template('results.html', class_id=pred_class, category=pred_cls_name, confi=conf_scr)


@app.route('/index')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    # app.run(debug=True, port=os.getenv('PORT', 5000))
    app.run(threaded=True, port=5000)
