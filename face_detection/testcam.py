import cv2

# Mở camera (0 là ID mặc định cho webcam đầu tiên)
cap = cv2.VideoCapture(0)

while True:
    # Đọc một frame từ camera
    ret, frame = cap.read()
    
    # Nếu đọc thành công, hiển thị frame
    if ret:
        cv2.imshow("Camera", frame)
    
    # Nhấn phím 'q' để thoát
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng camera và đóng cửa sổ
cap.release()
cv2.destroyAllWindows()
