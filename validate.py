# Copyright 2024 antillia.com Toshiyuki Arai
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# validate.py

import os
import cv2
import shutil
import glob
import traceback
import numpy as np
from PIL import Image, ImageOps

def pil2cv(image):
    new_image = np.array(image, dtype=np.uint8)
    if new_image.ndim == 2: 
        pass
    elif new_image.shape[2] == 3: 
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    elif new_image.shape[2] == 4: 
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    return new_image

def validate(images_dir, masks_dir, output_dir):
  image_files = glob.glob(images_dir + "/*.jpg")
  mask_files  = glob.glob(masks_dir  + "/*.jpg")
  image_files = sorted(image_files)
  mask_files  = sorted(mask_files)

  num_images = len(image_files)
  num_masks  = len(mask_files)

  if num_images != num_masks:
    raise Exception("Error ")
  for i in range(num_images):
    image_file = image_files[i]
    mask_file  = mask_files[i]
    basename = os.path.basename(image_file)
    image = Image.open(image_file)
    image = image.convert("RGB")
    image = pil2cv(image)
    #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mask  = Image.open(mask_file)
    mask  = mask.convert("L")
    #mask = cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)
    mask =  ImageOps.colorize(mask, black="black", white="green")
    mask = mask.convert("RGB")
    mask = pil2cv(mask)
    image += mask
    blended_filepath = os.path.join(output_dir, basename)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(blended_filepath, image)
    print("--- saved {}".format(blended_filepath))

if __name__ == "__main__":
  try:
    images_dir = "./HepaticVessel-ImageMask-Dataset-V1/train/images"
    masks_dir  = "./HepaticVessel-ImageMask-Dataset-V1/train/masks"
    output_dir = "./HepaticVessel-train-blended"

    if os.path.exists(output_dir):
      shutil.rmtree(output_dir)   

    if not os.path.exists(output_dir):
      os.makedirs(output_dir)   

    validate(images_dir, masks_dir, output_dir)

  except:
    traceback.print_exc()