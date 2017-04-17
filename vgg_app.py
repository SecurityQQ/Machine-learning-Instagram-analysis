
# coding: utf-8

# In[1]:

from vgg16 import vgg16
import tensorflow as tf
import numpy as np
import time   
from tqdm import tqdm
from scipy.misc import imread, imresize
from imagenet_classes import class_names
from PIL import Image
from resizeimage import resizeimage
import glob
import os
import sys


# In[4]:

def predict(X):
    old_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    results = []
    sess = tf.Session()
    img_shape = [None, X[0].shape[0],  X[0].shape[0], 3]
    imgs = tf.placeholder(tf.float32, img_shape)
    vgg = vgg16(imgs, 'vgg16_weights.npz', sess)
    for img in X:
        img_for_processing = imresize(img, X[0].shape)
        prob = sess.run(vgg.probs, feed_dict={vgg.imgs: [img_for_processing]})[0]
        preds = (np.argsort(prob)[::-1])[0:5]
        result = list(map(lambda p: (class_names[p], prob[p]), preds))
        results += result
    sys.stdout = old_stdout
    return results


# In[5]:

def predict_user(username):
    photos = []
    for img in glob.glob(username + '/*.jpg'):
        photo = imread(img, mode='RGB')
        photo = imresize(photo, (224, 224))
#         photo = imresize(photo, (photo.shape[0], photo.shape[1]))
        photos.append(photo)
    if len(photos) > 0:
        return process_results(predict(photos))
    else:
        return {"no photos": 0}
        


# In[6]:

# results = predict_user('alexm.shots')


# In[32]:

def process_results(results):
    classes = {}
    norm_const = 0
    for obj in results:
        norm_const += obj[1]
        if obj[0] in classes:
            classes[obj[0]] += obj[1]
        else:
            classes[obj[0]] = obj[1]
    return dict(map(lambda (k,v): (k, v / norm_const), classes.iteritems()))
            


# In[16]:

# results = process_result(results)


# In[30]:

# eps = 1e-6
# assert(np.sum(results.values()) > 1-eps and np.sum(results.values()) < 1 + eps)


# In[31]:

# results


# In[ ]:



