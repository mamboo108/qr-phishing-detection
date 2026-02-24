import cv2
import numpy as np
import pickle

model = pickle.load(open("qr_model.pkl","rb"))
detector = cv2.QRCodeDetector()

def preprocess(img):
    img = cv2.resize(img, (400,400))
    img = cv2.GaussianBlur(img,(3,3),0)
    return img

def get_features(img):

    img = preprocess(img)

    data, _, _ = detector.detectAndDecode(img)
    decodable = 1 if data != "" else 0

    h, w = img.shape
    img[int(h*0.4):int(h*0.6), int(w*0.4):int(w*0.6)] = 255

    ratio = np.sum(img < 128) / img.size
    variance = np.var(img)
    symmetry = np.mean(img == cv2.flip(img,1))
    noise = np.std(cv2.GaussianBlur(img,(5,5),0) - img)
    size = img.shape[0]

    edges = cv2.Canny(img,100,200)
    edge_density = np.sum(edges>0) / img.size

    contours,_ = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contour_count = len(contours)

    quiet_zone = np.mean(img[0:15,:] == 255)
    blur = cv2.Laplacian(img,cv2.CV_64F).var()

    return [
        ratio, variance, symmetry, noise, size,
        edge_density, contour_count, quiet_zone,
        blur, decodable
    ]

def analyze_qr(path):

    img = cv2.imread(path,0)
    if img is None:
        return "Invalid image"

    feats = get_features(img)
    pred = model.predict([feats])[0]

    return "✅ SAFE QR" if pred==0 else "❌ FAKE QR"