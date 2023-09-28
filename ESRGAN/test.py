import os.path as osp
import glob
import cv2
import numpy as np
import torch
from ESRGAN  import RRDBNet_arch as arch
from PIL import Image

import os
def call_srgan(username,imgpath):


    model_path = 'C:/Users/Asus/Downloads/DjangoProject_AevolveAI_Beta/ESRGAN/models/RRDB_ESRGAN_x4.pth'  # models/RRDB_ESRGAN_x4.pth OR models/RRDB_PSNR_x4.pth
    # device = torch.device('cuda')  # if you want to run on CPU, change 'cuda' -> cpu
    device = torch.device('cpu')
    #imgpath=imgpath
    ##img = Image.open(imgpath)
    #print("Imagename :" ,img.filename)
    #imgpath1=imgpath.split('/')[0]
    #imgpath2 = imgpath.split('/')[1]
    #fname=imgpath.split('/')[2]
    #imgform['image'].value()
    fname=str(imgpath)
    #print('user:', username)
    test_img_folder = 'C:/Users/Asus/Downloads/DjangoProject_AevolveAI_Beta/media/ESRGAN/LR/'+username+'/'+fname

    model = arch.RRDBNet(3, 3, 64, 23, gc=32)
    model.load_state_dict(torch.load(model_path), strict=True)
    model.eval()
    model = model.to(device)

    print('Model path {:s}. \nTesting...'.format(model_path))

    idx = 0
    for path in glob.glob(test_img_folder):
        idx += 1
        base = osp.splitext(osp.basename(path))[0]
        print(idx, base)
        # read images
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        img = img * 1.0 / 255
        img = torch.from_numpy(np.transpose(img[:, :, [2, 1, 0]], (2, 0, 1))).float()
        img_LR = img.unsqueeze(0)
        img_LR = img_LR.to(device)

        with torch.no_grad():
            output = model(img_LR).data.squeeze().float().cpu().clamp_(0, 1).numpy()
        output = np.transpose(output[[2, 1, 0], :, :], (1, 2, 0))
        output = (output * 255.0).round()
        os.makedirs('C:/Users/Asus/Downloads/DjangoProject_AevolveAI_Beta/ESRGAN/results/'+username,exist_ok=True)
        cv2.imwrite('C:/Users/Asus/Downloads/DjangoProject_AevolveAI_Beta/ESRGAN/results/'+username+'/'+'{:s}_rlt.png'.format(base), output)
        #cv2.imshow('test', output)

        # waits for user to press any key
        # (this is necessary to avoid Python kernel form crashing)
        #cv2.waitKey(0)

        # closing all open windows
        #cv2.destroyAllWindows()
