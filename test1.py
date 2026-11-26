import cv2
img = cv2.imread("screenshot.png")   # 读你之前按S保存的图
print(img.shape)    # 输出类似 (1080, 1920, 3)：高、宽、3通道
print(img[100, 200])  # 第100行200列那个像素的 [B, G, R] 三个数