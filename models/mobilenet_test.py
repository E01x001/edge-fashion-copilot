# upload_only.py
import torch
from torchvision.models import mobilenet_v2
import qai_hub as hub

model = mobilenet_v2(weights='DEFAULT')
model.eval()
traced_model = torch.jit.trace(model, torch.rand(1, 3, 224, 224))

uploaded_model = hub.upload_model(traced_model)
print(f"Model uploaded with ID: {uploaded_model.model_id}")