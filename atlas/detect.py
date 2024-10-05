from PIL import Image
from ultralytics import YOLO
from pathlib import Path

import ultralytics
ultralytics.checks()

def detectInPath(zoom):
    test_imgs = Path(str(zoom)).glob('**/*.tif')
    test_imgs = [str(x) for x in test_imgs]
    print(len(test_imgs))
    #https://huggingface.co/mayrajeo/marine-vessel-detection-yolov8
    # Other models to test: https://github.com/swricci/small-boat-detector
    # From https://github.com/robmarkcole/kaggle-ships-in-Google-Earth-with-YOLOv8/blob/main/models/yolov8m_best.pt
    model = YOLO(f'models\marine-vessel-detection-yolov8\yolov8s.pt')
    model.predict(source=test_imgs, conf=0.2, save=True)