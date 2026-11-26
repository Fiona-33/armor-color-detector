"""
装甲板灯条颜色识别与追踪
流程：高斯滤波 -> HSV阈值分割 -> 形态学去噪 -> 轮廓几何筛选 -> 输出目标中心
按 S 保存当前帧截图
"""
import cv2
import numpy as np
import time

def nothing(x):
    pass

def detect_target(frame, lower, upper, kernel_size=5, min_area=500,
                  ratio_range=(0.2, 5.0)):
    """输入一帧 BGR 图像，返回标注后的图、掩膜、目标中心列表"""
    blur = cv2.GaussianBlur(frame, (5, 5), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)  # 开运算去噪点
    mask = cv2.dilate(mask, kernel, iterations=2)           # 膨胀连通目标
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    centers = []
    for c in contours:
        if cv2.contourArea(c) < min_area:                   # 面积过滤
            continue
        x, y, w, h = cv2.boundingRect(c)
        if not (ratio_range[0] < w / h < ratio_range[1]):   # 长宽比过滤
            continue
        cx, cy = x + w // 2, y + h // 2
        centers.append((cx, cy))
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
        cv2.putText(frame, f"({cx},{cy})", (x, y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return frame, mask, centers

def main(source=0):
    # source=0 用摄像头；传视频路径则用视频文件，如 "demo.mp4"
    cap = cv2.VideoCapture(source)

    # 调参面板：蓝色默认阈值（H 100~130）
    cv2.namedWindow("panel")
    cv2.createTrackbar("H_min", "panel", 100, 180, nothing)
    cv2.createTrackbar("H_max", "panel", 130, 180, nothing)
    cv2.createTrackbar("S_min", "panel", 120, 255, nothing)
    cv2.createTrackbar("V_min", "panel", 70, 255, nothing)

    prev = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        h_min = cv2.getTrackbarPos("H_min", "panel")
        h_max = cv2.getTrackbarPos("H_max", "panel")
        s_min = cv2.getTrackbarPos("S_min", "panel")
        v_min = cv2.getTrackbarPos("V_min", "panel")

        frame, mask, centers = detect_target(
            frame, (h_min, s_min, v_min), (h_max, 255, 255))

        now = time.time()
        cv2.putText(frame, f"FPS: {1 / (now - prev):.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        prev = now

        cv2.imshow("result", frame)
        cv2.imshow("mask", mask)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            cv2.imwrite("screenshot.png", frame)
            print("已保存 screenshot.png")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()