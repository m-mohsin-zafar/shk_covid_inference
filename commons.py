import os
import io
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
from networks import CovidRENet


class Commons:
    def __init__(self):
        self.model_path = os.path.join(os.getcwd(), 'checkpoints', 'CovidRENet__best_weights.pth')
        self.transformations = transforms.Compose([
            transforms.Resize((128, 128)),
            transforms.ToTensor()])

    def prepare_model(self):
        model = CovidRENet()
        model.load_state_dict(torch.load(self.model_path, map_location='cpu'), strict=False)
        model.eval()
        return model

    def preprocess(self, image_bytes):
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        except Exception:
            return 0, 'Something wrong with Image PreProcessing'

        return self.transformations(image).unsqueeze(0)
