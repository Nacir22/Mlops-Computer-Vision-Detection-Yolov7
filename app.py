import sys,os
from isd.pipeline.training_pipeline import TrainPipeline
from isd.exception import isdException
from isd.logger import logging
from isd.utils.main_utils import decodeImage, encodeImageIntoBase64
from flask import Flask, request, jsonify, render_template,Response
from flask_cors import CORS, cross_origin



app = Flask(__name__)
CORS(app)


class ClientApp:
    def __init__(self):
        self.filename = "inputImage.jpg"



@app.route("/train")
def trainRoute():
    obj = TrainPipeline()
    obj.run_pipeline()
    return 
    


@app.route("/")
def home():
    return render_template("index.html")



@app.route("/predict", methods=['POST','GET'])
@cross_origin()
def predictRoute():
    try:
        image = request.json['image']
        decodeImage(image, clApp.filename)

       
        os.system("cd yolov7/ && python detect.py --weights my_model.pt  --source ../data/inputImage.jpg")

        opencodedbase64 = encodeImageIntoBase64("yolov7/runs/detect/exp/inputImage.jpg")
        result = {"image": opencodedbase64.decode('utf-8')}
        os.system("rm -rf yolov7/runs")

    except ValueError as val:
        logging.error(f"ValueError in predictRoute: {val}")
        return Response("Value not found inside  json data")
    except KeyError:
        logging.error("KeyError in predictRoute: incorrect key passed")
        return Response("Key value error incorrect key passed")
    except Exception as e:
        logging.error(f"Unexpected error in predictRoute: {e}")
        result = "Invalid input"

    return jsonify(result)


if __name__ == "__main__":
    clApp = ClientApp()
    app.run(host="0.0.0.0", port=8080)
    

