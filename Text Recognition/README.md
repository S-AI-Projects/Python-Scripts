# Image Text Recognition ML Model

The notebook recognizes handwritten text in an image using the
`microsoft/trocr-large-handwritten` model.

## Input and result

`recognize_text(image_url)` accepts an image URL and returns the first decoded
transcription as a string. The notebook uses the example URL in
`text_recognition.py` and prints the returned text.

## State and dependencies

Each call creates its own image, processor, and model objects; it does not
reuse or mutate objects from an earlier call. The preceding pipeline demo cell
in the notebook creates its own `pipe` global, which `recognize_text` does not
use. Transformers may populate its local model cache.

The notebook needs Python with `transformers`, `requests`, Pillow, and PyTorch.
Its install cell installs `transformers`; the other packages must also be
available in the environment. Image and model downloads require network access.

To run the notebook, start Jupyter with this directory as its working
directory, open the notebook, and execute its cells.