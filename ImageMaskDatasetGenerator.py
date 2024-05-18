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

# 2024/05/17


import os
import sys
import shutil
from PIL import Image
import glob
import numpy as np
import math
import nibabel as nib
import traceback

# Read file
"""
scan = nib.load('/path/to/stackOfimages.nii.gz')
# Get raw data
scan = scan.get_fdata()
print(scan.shape)
(num, width, height)

"""


class ImageMaskDatasetGenerator:

  def __init__(self, images_dir, labels_dir, output_images_dir, output_masks_dir):
    self.images_dir = images_dir
    self.labels_dir = labels_dir
    self.output_images_dir = output_images_dir
    self.output_masks_dir  = output_masks_dir
    self.angle     = 90
    self.RESIZE    = (512, 512)
       
  def create_mask_files(self, img_file, name, output_dir, index):
    print("--- niigz {}".format(img_file))
    img = nib.load(img_file)
    
    data = img.get_fdata()
    print("---create_mask_files data shape {} ".format(data.shape))
    shape = data.shape
    if len(shape) == 4:
      data = data.reshape((shape[0], shape[1], shape[2]))
    print("--- data.shape {}".format(data.shape))
    num_images = data.shape[2] 
    print("--- num_images {}".format(num_images))
    num = 0  
    for i in range(num_images):
      img = data[:,:,i]
      img = np.array(img)*255.0      
      img = img.astype("uint8") 
      filename = str(index + i) + "_" + name + ".jpg"
      filepath = os.path.join(output_dir, filename)
      if np.any(img > 0):
        img = Image.fromarray(img)
        img = img.convert("RGB")
        img = img.resize(self.RESIZE)
        if self.angle > 0:
          img = img.rotate(self.angle)
        img.save(filepath)
        print("Saved {}".format(filepath))
        num += 1
    return num
  
  def normalize(self, image):
    min = np.min(image)/255.0
    max = np.max(image)/255.0
    scale = (max - min)
    image = (image - min) / scale
    image = image.astype('uint8') 
    return image   

  def create_image_files(self, image_file, name, output_masks_dir, output_images_dir, index):
    img = nib.load(image_file)

    data = img.get_fdata()
    print("---create_image_files data shape {} ".format(data.shape))
    print("--- shape {}".format(data.shape))

    shape = data.shape
  
    if len(shape) == 4:
      data = data.reshape((shape[0], shape[1], shape[2]))

    num_images = data.shape[2] # 
    print("--- num_images {}".format(num_images))
    num = 0
    for i in range(num_images):
      img = data[:,:,i]
      
      filename = str(index + i) + "_" + name + ".jpg"
      filepath = os.path.join(output_images_dir, filename)
      mask_filepath = os.path.join(output_masks_dir, filename)
      
      if os.path.exists(mask_filepath):
        # 2024/02/20  
        #img = self.normalize(img)
        img = Image.fromarray(img)
        img = img.convert("RGB")
        img = img.resize(self.RESIZE)
        if self.angle>0:
          img = img.rotate(self.angle)
        img.save(filepath)
        print("Saved {}".format(filepath))
        num += 1
    return num
  

  def generate(self):

    image_files = glob.glob(self.images_dir + "/hepaticvessel_*.nii.gz")
    index = 10000
    print("=== generate image_files {}".format(image_files))
    for image_file in image_files:
        basename  = os.path.basename(image_file)
        name      = basename.split(".")[0]
        img_name  = basename.split(".")[0]
        mask_name = basename
        mask_file = os.path.join(self.labels_dir, mask_name)
        print("---image file {}".format(image_file))

        print("---mask file {}".format(mask_file))
        
        # 1 create mask files at first. 
        num_masks  = self.create_mask_files(mask_file,   name, self.output_masks_dir,  index)
        # 2 create image files if mask files exist.
        num_images = self.create_image_files(image_file, name, self.output_masks_dir, 
                                             self.output_images_dir, index)
        print(" num_images: {}  num_masks: {}".format(num_images, num_masks))


if __name__ == "__main__":
  try:
    images_dir        = "./Task08_HepaticVessel/ImagesTr"
    labels_dir        = "./Task08_HepaticVessel/LabelsTr"
    output_images_dir = "./HepaticVessel-master/train/images/"
    output_masks_dir  = "./HepaticVessel-master/train/masks/"

    if os.path.exists(output_images_dir):
      shutil.rmtree(output_images_dir)
    if not os.path.exists(output_images_dir):
      os.makedirs(output_images_dir)

    if os.path.exists(output_masks_dir):
      shutil.rmtree(output_masks_dir)
    if not os.path.exists(output_masks_dir):
      os.makedirs(output_masks_dir)

    # Create jpg image and mask files from nii.gz files under data_dir.                                           
    generator = ImageMaskDatasetGenerator(images_dir, labels_dir, 
                                          output_images_dir, output_masks_dir)
    generator.generate()

  except:
    traceback.print_exc()


