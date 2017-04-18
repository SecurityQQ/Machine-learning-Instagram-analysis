
# coding: utf-8

# In[2]:

# set up Python environment: numpy for numerical routines, and matplotlib for plotting
import numpy as np
import os
from tqdm import tqdm
import glob
from scipy.misc import imread, imresize
import matplotlib.pyplot as plt
import sys

old_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')

root = '/home/zerts/MIPT/Machine-learning-Instagram-analysis/predict_system'
# root= os.getcwd()


# set display defaults
plt.rcParams['figure.figsize'] = (10, 10)        # large images
plt.rcParams['image.interpolation'] = 'nearest'  # don't interpolate: show square pixels
plt.rcParams['image.cmap'] = 'gray'  # use grayscale output rather than a (potentially misleading) color heatmap


# In[3]:

import sys
caffe_root = '/home/valeriyasin/Programms/caffe/'  # this file should be run from {caffe_root}/examples (otherwise change this line)
sys.path.insert(0, caffe_root + 'python')
os.chdir(caffe_root)
import caffe


import os
if os.path.isfile(caffe_root + 'models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel'):
    print 'CaffeNet found.'
else:
    print 'Downloading pre-trained CaffeNet model...'
    get_ipython().system('../scripts/download_model_binary.py ../models/bvlc_reference_caffenet')

caffe.set_mode_cpu()

model_def = caffe_root + 'models/finetune_flickr_style/deploy.prototxt'
model_weights = caffe_root +  'models/finetune_flickr_style/finetune_flickr_style.caffemodel'

net = caffe.Net(model_def,      # defines the structure of the model
                model_weights,  # contains the trained weights
                caffe.TEST)     # use test mode (e.g., don't perform dropout)



# load the mean ImageNet image (as distributed with Caffe) for subtraction
mu = np.load(caffe_root + 'python/caffe/imagenet/ilsvrc_2012_mean.npy')
mu = mu.mean(1).mean(1)  # average over pixels to obtain the mean (BGR) pixel values
print 'mean-subtracted values:', zip('BGR', mu)

# create transformer for the input called 'data'
transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})

transformer.set_transpose('data', (2,0,1))  # move image channels to outermost dimension
transformer.set_mean('data', mu)            # subtract the dataset-mean value in each channel
transformer.set_raw_scale('data', 255)      # rescale from [0, 1] to [0, 255]
transformer.set_channel_swap('data', (2,1,0))  # swap channels from RGB to BGR


# In[7]:

labels_file = caffe_root + 'examples/finetune_flickr_style/style_names.txt'
if not os.path.exists(labels_file):
    get_ipython().system('../data/ilsvrc12/get_ilsvrc_aux.sh')
    
labels = np.loadtxt(labels_file, str, delimiter='\t')


sys.stdout = old_stdout


# In[9]:

def predict(X):
    old_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w') 
    results = []
    for img in X:
        transformed_image = transformer.preprocess('data', img)
        net.blobs['data'].data[...] = transformed_image
        output = net.forward()
        output_prob = output['prob'][0]
        top_inds = output_prob.argsort()[::-1][:5]  # reverse sort and take five largest items
        result = list(map(lambda x: (labels[x], output_prob[x]), top_inds))  
        results += result
    sys.stdout = old_stdout
    return results


# In[24]:

def predict_user(username):
    photos = []
    print(root + '/' +  username + '/*.jpg')
    for img in glob.glob(root + '/' +  username + '/*.jpg'):
        photo = imread(img, mode='RGB')
        photo = imresize(photo, (photo.shape[0], photo.shape[1]))
        photos.append(photo)
    if len(photos) > 0:
        return process_results(predict(photos))
    else:
        return {"no photos": 0}


# In[25]:

#results = predict_user('alexm.shots')


# In[28]:

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


# In[29]:

# results


# In[30]:

# presults = process_result(results)


# In[36]:

# eps = 1e-6
# assert(np.sum(presults.values()) > 1-eps and np.sum(presults.values()) < 1 + eps)


# In[34]:

# presults


# In[ ]:



