# import the inference-sdk
from inference_sdk import InferenceHTTPClient
import cv2
import supervision as sv
import os
from dotenv import load_dotenv

# initialize the client
load_dotenv()
API_KEY = os.getenv("ROBOFLOW_API_KEY")
CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=API_KEY
)

# infer on a local image
result = CLIENT.infer("13.841102_100.576260_ZeNDRe7dEJ8Jip8atqUj9A_299_2025-08.jpg", model_id="sidewalk-segmentation-wj5dv/3")
print(result)
image = cv2.imread("13.841102_100.576260_ZeNDRe7dEJ8Jip8atqUj9A_299_2025-08.jpg")

# 2. Convert the API result into a format Supervision understands
detections = sv.Detections.from_inference(result)

# 3. Create annotators (Masks and Labels)
mask_annotator = sv.MaskAnnotator()
label_annotator = sv.LabelAnnotator()

# 4. Draw the masks and labels on the image
annotated_image = mask_annotator.annotate(scene=image, detections=detections)
annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections)

# 5. Show the image
sv.plot_image(annotated_image)
# OR save it to a file
cv2.imwrite("output_result.jpg", annotated_image)