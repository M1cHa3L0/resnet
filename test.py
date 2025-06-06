"""
main file
1. load data
2. model
3. train
4. test and eval
5. save
"""
import torch
from torch import nn
import os
from torchvision import transforms, datasets
from torchvision.transforms import ToTensor
import data_setup, train, ResNet, utils
from torch.utils.data import DataLoader
import torchvision.models as models
import pandas as pd


# device agnostic code
device = 'cuda' if torch.cuda.is_available() else 'cpu'
# hyperparameters
EPOCHS = 10
BATCH_SIZE = 128
NUM_WORKERS = 4
LR = 0.001
HIDDEN_UNITS = 0
TRAIN_RATIO = 0.8


# data transforms
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    # transforms.TrivialAugmentWide(num_magnitude_bins=31) # data augmentation
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]) # 标准化
])

# load data
train_data = datasets.Food101(
    root='resnet/data/food101',
    split='train',
    transform=transform,
    target_transform=False,
    download=True # False if downloaded
)

test_data = datasets.Food101(
    root='resnet/data/food101',
    split='test',
    transform=transform,
    download=True) # False if downloaded

train_dataloader, test_dataloader, class_names = data_setup.create_dataLoader(transforms=transform,
                                                                              batch_size=BATCH_SIZE,
                                                                              train_data=train_data,
                                                                              test_data=test_data)

# subset of food101
'''
data_file = "https://github.com/mrdbourke/pytorch-deep-learning/raw/refs/heads/main/data/pizza_steak_sushi.zip"
train_dir = 'resnet/data/pizza_steak_sushi/train'
test_dir = 'resnet/data/pizza_steak_sushi/test'
train_dataloader, test_dataloader, class_names = data_setup.create_dataLoader(train_dir=train_dir,
                                                                              test_dir=train_dir,
                                                                              transforms=transform,
                                                                              batch_size=BATCH_SIZE,
                                                                              num_workers=NUM_WORKERS)
'''

#print(class_names)
#print(len(train_dataloader.dataset))


# data_setup.split()

# load model and pretrained model
pretrained_resnet50 = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
in_features = pretrained_resnet50.fc.in_features 
pretrained_resnet50.fc = nn.Linear(in_features, 101) # change pretrained model output class to 101
# load pretrained model parameters
resnet50model = ResNet.ResNet50(num_classes=len(class_names)).to(device)
resnet50model.load_state_dict(pretrained_resnet50.state_dict(), strict=False)

# loss func and optimier
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(params=resnet50model.parameters(), lr=LR)

# save results
results = train(resnet50model, train_dataloader, test_dataloader, loss_fn, optimizer, EPOCHS, device)
print(results)

# plot loss
utils.plot_loss_curve(results)

# save model
utils.save_model(resnet50model, 'resnet/models', 'resnet50model.pth')
