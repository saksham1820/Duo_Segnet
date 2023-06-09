import os
from PIL import Image
import pdb
import torch.utils.data as data
from torchvision.transforms import transforms


class ObjDataset(data.Dataset):
    def __init__(self, images, gts, trainsize):
        #pdb.set_trace()
        self.trainsize = trainsize
        self.images = images
        self.gts = gts
        self.images = sorted(self.images)
        self.gts = sorted(self.gts)
        #self.filter_files()
        self.size = len(self.images)
        self.img_transform = transforms.Compose([
            transforms.Resize((self.trainsize, self.trainsize)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
        self.gt_transform = transforms.Compose([
            transforms.Resize((self.trainsize, self.trainsize)),
            transforms.ToTensor()])
        #pdb.set_trace()

    def __getitem__(self, index):
        image = self.rgb_loader(self.images[index])
        gt = self.binary_loader(self.gts[index])

        image = self.img_transform(image)
        gt = self.gt_transform(gt)
        #pdb.set_trace()
        return image, gt

    def filter_files(self):
        assert len(self.images) == len(self.gts)
        images = []
        gts = []
        for img_path, gt_path in zip(self.images, self.gts):
            img = Image.open(img_path)
            gt = Image.open(gt_path)
            if img.size == gt.size:
                images.append(img_path)
                gts.append(gt_path)
        self.images = images
        self.gts = gts

    def rgb_loader(self, path):
        with open(path, 'rb') as f:
            img = Image.open(f)
            #pdb.set_trace()
            return img.convert('RGB')

    def binary_loader(self, path):
        with open(path, 'rb') as f:
            img = Image.open(f)
            # return img.convert('1')
            #pdb.set_trace()
            return img.convert('L')

    def resize(self, img, gt):
        assert img.size == gt.size
        w, h = img.size
        if h < self.trainsize or w < self.trainsize:
            h = max(h, self.trainsize)
            w = max(w, self.trainsize)
            #pdb.set_trace()
            return img.resize((w, h), Image.BILINEAR), gt.resize((w, h), Image.NEAREST)
        else:
            #pdb.set_trace()
            return img, gt

    def __len__(self):
        #pdb.set_trace()
        return self.size


class ValObjDataset(data.Dataset):
    def __init__(self, images, gts, trainsize):
        self.trainsize = trainsize
        self.images = images
        self.gts = gts
        self.images = sorted(self.images)
        self.gts = sorted(self.gts)
        self.filter_files()
        self.size = len(self.images)
        self.img_transform = transforms.Compose([
            transforms.Resize((self.trainsize, self.trainsize)),
            transforms.ToTensor()])
        self.gt_transform = transforms.Compose([
            transforms.Resize((self.trainsize, self.trainsize)),
            transforms.ToTensor()])

    def __getitem__(self, index):
        image = self.rgb_loader(self.images[index])
        gt = self.binary_loader(self.gts[index])

        image = self.img_transform(image)
        gt = self.gt_transform(gt)

        return image, gt

    def filter_files(self):
        assert len(self.images) == len(self.gts)
        images = []
        gts = []
        for img_path, gt_path in zip(self.images, self.gts):
            img = Image.open(img_path)
            gt = Image.open(gt_path)
            if img.size == gt.size:
                images.append(img_path)
                gts.append(gt_path)
        self.images = images
        self.gts = gts

    def rgb_loader(self, path):
        with open(path, 'rb') as f:
            img = Image.open(f)
            return img.convert('RGB')

    def binary_loader(self, path):
        with open(path, 'rb') as f:
            img = Image.open(f)
            # return img.convert('1')
            return img.convert('L')

    def resize(self, img, gt):
        assert img.size == gt.size
        w, h = img.size
        if h < self.trainsize or w < self.trainsize:
            h = max(h, self.trainsize)
            w = max(w, self.trainsize)
            return img.resize((w, h), Image.BILINEAR), gt.resize((w, h), Image.NEAREST)
        else:
            return img, gt

    def __len__(self):
        return self.size


def image_loader(image_root, gt_root, batch_size, image_size, split=0.8, labeled_ratio=0.05):
    #pdb.set_trace()
    images = ['../data/nuclei/train/image/' + f for f in os.listdir(image_root) if f.endswith('.jpg') or f.endswith('.png')]
    gts = ['../data/nuclei/train/mask/' + f for f in os.listdir(gt_root) if f.endswith('.jpg') or f.endswith('.png')]
    #pdb.set_trace()
    train_images = images[0:int(len(images) * split)]
    val_images = images[int(len(images) * split):]
    train_gts = gts[0:int(len(images) * split)]
    val_gts = gts[int(len(images) * split):]

    labeled_train_images = train_images[0:int(len(train_images) * labeled_ratio)]
    labeled_train_images_1 = labeled_train_images[0:int(len(labeled_train_images) * 0.5)]
    labeled_train_images_2 = labeled_train_images[int(len(labeled_train_images) * 0.5):]
    unlabeled_train_images = train_images[int(len(train_images) * labeled_ratio):]
    labeled_train_gts = train_gts[0:int(len(train_gts) * labeled_ratio)]
    labeled_train_gts_1 = labeled_train_gts[0:int(len(labeled_train_gts) * 0.5)]
    labeled_train_gts_2 = labeled_train_gts[int(len(labeled_train_gts) * 0.5):]
    unlabeled_train_gts = train_gts[int(len(train_gts) * labeled_ratio):]
    #pdb.set_trace()
    labeled_train_dataset_1 = ObjDataset(labeled_train_images_1, labeled_train_gts_1, image_size)
    labeled_train_dataset_2 = ObjDataset(labeled_train_images_2, labeled_train_gts_2, image_size)
    unlabeled_train_dataset = ObjDataset(unlabeled_train_images, unlabeled_train_gts, image_size)
    val_dataset = ValObjDataset(val_images, val_gts, image_size)
    #pdb.set_trace()
    labeled_data_loader_1 = data.DataLoader(dataset=labeled_train_dataset_1,
                                  batch_size=batch_size,
                                  num_workers=1,
                                  pin_memory=True,
                                  shuffle=True)

    labeled_data_loader_2 = data.DataLoader(dataset=labeled_train_dataset_2,
                                            batch_size=batch_size,
                                            num_workers=1,
                                            pin_memory=True,
                                            shuffle=True)

    unlabeled_data_loader = data.DataLoader(dataset=unlabeled_train_dataset,
                                          batch_size=batch_size,
                                          num_workers=1,
                                          pin_memory=True,
                                          shuffle=True)

    val_loader = data.DataLoader(dataset=val_dataset,
                                 batch_size=batch_size,
                                 num_workers=1,
                                 pin_memory=True,
                                 shuffle=False)

    return labeled_data_loader_1, labeled_data_loader_2, unlabeled_data_loader, val_loader
