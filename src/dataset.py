import numpy as np
from torch.utils.data import Dataset
import cv2
import os
from PIL import Image
from data.imgaug import GetTransforms
from data.utils import transform
# np.random.seed(0)


class ImageDataset(Dataset):
    def __init__(self, label_path, cfg, mode='train'):
        self.cfg = cfg
        self._label_header = None
        self._image_paths = []
        self._labels = []
        self._mode = mode
#         self.dict = [{'1.0': '1', '': '0', '0.0': '0', '-1.0': '0'},
#                      {'1.0': '1', '': '0', '0.0': '0', '-1.0': '-1'},
#                      {'1.0': '1', '': '0', '0.0': '0', '-1.0': '-1'},]
        self.dict = {'1.0': 1, '': 0, '0.0': 0, '-1.0': -1}
        with open(label_path) as f:
            header = f.readline().strip('\n').split(',')
            self._label_header = [
                header[7],
                header[10],
                header[11],
                header[13],
                'Pleural_Effusion']
            for line in f:
                labels = []
                fields = line.strip('\n').split(',')
                image_path = fields[0]
                flg_enhance = False
                for index, value in enumerate(fields[5:]):
#                     if index == 5 or index == 8:
#                         labels.append(self.dict[1].get(value))
#                         if self.dict[1].get(
#                                 value) == '1' and \
#                                 self.cfg.enhance_index.count(index) > 0:
#                             flg_enhance = True
#                     elif index == 2 or index == 6 or index == 10:
#                         labels.append(self.dict[0].get(value))
#                         if self.dict[0].get(
#                                 value) == '1' and \
#                                 self.cfg.enhance_index.count(index) > 0:
#                             flg_enhance = True
                # labels = ([self.dict.get(n, n) for n in fields[5:]])
                
                    if index == 2 or index == 5 or index == 8:
                        ## U-ones+LSR
                        label = self.dict.get(value)
                        if label == -1:
                            label = np.random.uniform(0.55,0.85)
                            
                        labels.append(label)
                        if label == 1 and self.cfg.enhance_index.count(index) > 0:
                            flg_enhance = True
                        
                    elif index == 6:
                        ## U-zeros +LSR
                        label =self.dict.get(value)
                        if label == -1:
                            label = np.random.uniform(0,0.3)
                            
                        labels.append(label)
                        if label == 1 and self.cfg.enhance_index.count(index) > 0:
                            flg_enhance = True
                    elif index == 10:
                        ## U-zeros
                        label = self.dict.get(value)
                        if label == -1:
                            label = 0
                            
                        labels.append(label)
                        if label == 1 and self.cfg.enhance_index.count(index) > 0:
                            flg_enhance = True
                        
                labels = list(map(float, labels))
                if mode == 'train' or mode == 'dev':
                    image_path = "./logdir/classification/"+image_path
                
                self._image_paths.append(image_path)

                
                assert os.path.exists(image_path), image_path
                self._labels.append(labels)
                if flg_enhance and self._mode == 'train':
                    for i in range(self.cfg.enhance_times):
                        self._image_paths.append(image_path)
                        self._labels.append(labels)
        self._num_image = len(self._image_paths)

    def __len__(self):
        return self._num_image

    def __getitem__(self, idx):
     
        image = cv2.imread(self._image_paths[idx], 0)
        
        image = Image.fromarray(image)
        
        if self._mode == 'train':
            image = GetTransforms(image, type=self.cfg.use_transforms_type)
        image = np.array(image)
        image = transform(image, self.cfg)
        labels = np.array(self._labels[idx]).astype(np.float32)

        path = self._image_paths[idx]

        if self._mode == 'train' or self._mode == 'dev':
            return (image, labels)
        elif self._mode == 'test':
            return (image, path)
        elif self._mode == 'heatmap':
            return (image, path, labels)
        else:
            raise Exception('Unknown mode : {}'.format(self._mode))
