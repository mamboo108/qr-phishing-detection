import cv2
import numpy as np

def get_qr_features(img):
    """Standardized 9-feature extraction for both training and testing."""
    # 1. Standardize input (Ensures grayscale and fixed size)
    if len(img.shape) > 2:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(img, (400, 400))
    
    # 2. Pre-processing
    img_blur = cv2.GaussianBlur(img, (3, 3), 0)
    
    # 3. Structural features
    ratio = np.sum(img < 128) / img.size
    variance = np.var(img)
    symmetry = np.mean(img == cv2.flip(img, 1))
    noise = np.std(cv2.GaussianBlur(img, (5, 5), 0) - img)
    
    # 4. Edge and Contour analysis
    edges = cv2.Canny(img, 100, 200)
    edge_density = np.sum(edges > 0) / img.size
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # 5. Lighting and Quality
    white_border = np.mean(img[0:15,:] > 200)
    laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
    
    return [ratio, variance, symmetry, noise, 400, edge_density, len(contours), white_border, laplacian_var]