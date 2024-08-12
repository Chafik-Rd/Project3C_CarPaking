from yolov4.tf import YOLOv4
import time
import numpy as np
import os
import GetImage
import matplotlib.pyplot as plt

os.environ['TF_XLA_FLAGS'] = '--tf_xla_enable_xla_devices'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# yolo = YOLOv4()
yolo = YOLOv4(tiny=True)

yolo.classes = "coco.names"
yolo.input_size = (640, 480)

yolo.make_model()
# yolo.load_weights("yolov4.weights", weights_type="yolo")
yolo.load_weights("yolov4-tiny.weights", weights_type="yolo")

def intersection(obj, frames, IMG_HEIGHT, IMG_WIDTH):
    # x, y, w, h, class id, prob
    obj_left = (IMG_WIDTH*obj[0])-(IMG_WIDTH*obj[2]*0.5)
    obj_right = (IMG_WIDTH*obj[0])+(IMG_WIDTH*obj[2]*0.5)
    obj_top = (IMG_HEIGHT*obj[1])-(IMG_HEIGHT*obj[3]*0.5)
    obj_bottom = (IMG_HEIGHT*obj[1])+(IMG_HEIGHT*obj[3]*0.5)
    
    max_AOI = 0
    frame_area = -1
    frame_idx = -1
    
    for frame in frames:
        left = max(obj_left,frame[1])
        right = min(obj_right,frame[2])
        top = max(obj_top,frame[3])
        bottom = min(obj_bottom,frame[4])
        
        AOI = 0
        if (left < right and bottom > top):
            AOI = (right - left) * (bottom - top)

        if AOI > max_AOI:
            max_AOI = AOI
            frame_area = frame[5]
            frame_idx = frame[0]

    IOF = max_AOI/frame_area # Area of intersection over area of frame
    IOO = max_AOI/(obj[2]*obj[3]*IMG_HEIGHT*IMG_WIDTH) # Area of intersection over area of obj
        
    return IOF, IOO, frame_idx

def app(frames, img_todrawn=None):
    img = np.array(GetImage.getLastImg(True))
    # get=Image.open(r"D:\Project3C\Part 2\Project-3C\Project-3C_CarPaking\CodeTest\ggg.jpg")
    # img = np.array(get)
    IMG_WIDTH = img.shape[1]
    IMG_HEIGHT = img.shape[0]

    startTime= time.time()
    objs = yolo.predict(img)
    elapseTime = time.time() - startTime

    car = []
    pos = []
    for obj in objs:
        IOF, IOO, idx = intersection(obj, frames, IMG_HEIGHT, IMG_WIDTH)
        print("Intersection over frame :",IOF,", ","Intersection over obj :",IOO)
        if  IOF >= 0.5 and IOO >= 0.65 and obj[4] in [2., 5., 7.]:
            car.append(obj) 
            pos.append(idx)
        
    car = np.array(car)

    Available = []
    for i in range(len(frames)):
        if i not in pos:
            Available.append(i+1)
    print(Available)   
        
    try:
        if img_todrawn is not None:
            img = img_todrawn
        result = yolo.draw_bboxes(img,car)
        return result,Available,elapseTime
    except:
        return img,Available,elapseTime

    # yolo.inference(media_path="Cars Driving.mp4", is_image=False)

if __name__ == '__main__':

    fs = [[0, 399, 633, 305, 460, 36270], [1, 18, 208, 296, 442, 27740], [2, 219, 406, 296, 445, 27863]]
    result, Available,el = app(fs)
    plt.imshow(result)
    plt.show()
    print (Available)