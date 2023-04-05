import os

path = "/data/saksham/retinal_project/Duo-SegNet/data"
directories = os.listdir(path + "/train")

for i in range(len(directories)):
    file_loc = path + '/train/' + directories[i] + '/images/' + directories[i] + '.png' 
    dest_loc = path + '/train_images/' + directories[i] + '.png'
    #print(file_loc,'\n', dest_loc) 
    os.rename(file_loc, dest_loc)
    
