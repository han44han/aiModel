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
from huggingface_hub import hf_hub_download

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://fixneuro.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

IMAGE_SOLUTIONS = {
    "Cars": "الهيكل الخارجي للسيارة سليم بشكل عام.",
    "Broken part": "يوجد أجزاء مكسورة (Severe Damage). الحل: استبدال القطع المتضررة وسمكرة شاملة.",
    "Dent": "يوجد انبعاج (Dent). الحل: سمكرة على البارد أو شفط الصدمة.",
    "Scratch": "توجد خدوش (Scratch). الحل: تلميع أو رش تجميلي.",
    "Clean": "لم يتم اكتشاف أضرار واضحة."
}

# --- تعديل طريقة جلب الموديل ---
def get_model_file():
    # سيقوم بجلب التوكن من Environment Variables في ريندر
    hf_token = os.getenv("HF_TOKEN")
    
    # تحميل الموديل مباشرة من مستودعك في Hugging Face
    model_path = hf_hub_download(
        repo_id="han44han/aiModel",  # تأكدي أن هذا هو اسم حسابك والمستودع في HF
        filename="model_final.pth",
        token=hf_token
    )
    return model_path

# جلب المسار الصحيح للموديل
MODEL_PATH = get_model_file()

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 4 
cfg.MODEL.WEIGHTS = MODEL_PATH
cfg.MODEL.DEVICE = "cpu"
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.2 
predictor = DefaultPredictor(cfg)

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
        detected_labels = list(set([class_names[i] for i in pred_classes]))
        
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

if __name__ == "__main__":
    import uvicorn
    # ريندر يمرر البورت عبر متغير بيئة، لذا نستخدم os.getenv
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
