"""Stateless image-to-text inference for the Text Recognition notebook."""

MODEL_ID = "microsoft/trocr-large-handwritten"
DEFAULT_IMAGE_URL = "https://fki.tic.heia-fr.ch/static/img/a01-122-02-00.jpg"


def recognize_text(image_url: str) -> str:
    """Fetch an image URL and return the model's first decoded transcription."""
    import requests
    from PIL import Image
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel

    response = requests.get(image_url, stream=True)
    image = Image.open(response.raw).convert("RGB")
    processor = TrOCRProcessor.from_pretrained(MODEL_ID)
    model = VisionEncoderDecoderModel.from_pretrained(MODEL_ID)
    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    return processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
