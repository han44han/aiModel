import os
import requests
import numpy as np
import cv2
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2 import model_zoo

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://fixneuro.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# القاموس المحدث بناءً على كلاسات Kaggle الخاصة بك
IMAGE_SOLUTIONS = {
    "Cars": "الهيكل الخارجي للسيارة سليم بشكل عام.",
    "Broken part": "يوجد أجزاء مكسورة (Severe Damage). الحل: استبدال القطع المتضررة وسمكرة شاملة.",
    "Dent": "يوجد انبعاج (Dent). الحل: سمكرة على البارد أو شفط الصدمة.",
    "Scratch": "توجد خدوش (Scratch). الحل: تلميع أو رش تجميلي.",
    "Clean": "لم يتم اكتشاف أضرار واضحة."
}

def download_model():
    model_id = '1SCiXoupm2eDFLqzjUKH2b8KGT0zQwpCx'
    url = f'https://drive.google.com/uc?export=download&id={model_id}'
    output = 'model_final.pth'
    if not os.path.exists(output):
        response = requests.get(url, stream=True)
        with open(output, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    return output

MODEL_PATH = download_model()

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
# عدلنا العدد إلى 4 بناءً على صورتك من كاجل
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 4 
cfg.MODEL.WEIGHTS = MODEL_PATH
cfg.MODEL.DEVICE = "cpu"
# جعلنا الحساسية قوية جداً (0.2) ليكتشف أي ضرر بسيط
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.2 
predictor = DefaultPredictor(cfg)

# الترتيب الصحيح 100% من صورتك
class_names = ["Cars", "Broken part", "Dent", "Scratch"]

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    outputs = predictor(img)
    instances = outputs["instances"]
    
    if len(instances) > 0:
        pred_classes = instances.pred_classes.tolist()
        # جلب جميع التصنيفات المكتشفة
        detected_labels = list(set([class_names[i] for i in pred_classes]))
        
        # إذا اكتشف سيارة وأضرار، نظهر الأضرار فقط
        if len(detected_labels) > 1 and "Cars" in detected_labels:
            detected_labels.remove("Cars")
            
        res_class = " + ".join(detected_labels)
        solutions = [IMAGE_SOLUTIONS.get(label, "فحص فني.") for label in detected_labels]
        solution_text = " | ".join(solutions)
    else:
        res_class = "Clean"
        solution_text = IMAGE_SOLUTIONS["Clean"]

    return {
        "status": "success",
        "prediction": res_class,
        "solution": solution_text
    }

# كود تشخيص النص يبقى كما هو (أضيفيه هنا إذا أردتِ)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)