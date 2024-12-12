from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import HTMLResponse
import cv2
import os
from typing import Optional

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>QR Code Scanner</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .container {
                text-align: center;
                background: #ffffff;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #333333;
            }
            form {
                margin-top: 20px;
            }
            button {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #0056b3;
            }
            a {
                color: #007bff;
                text-decoration: none;
                margin-top: 20px;
                display: inline-block;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>QR Code Scanner</h1>
            <form action="/scan" method="post">
                <button type="submit">Start Scanning</button>
            </form>
        </div>
    </body>
    </html>
    """

def scan_qr_code_from_camera():
    """Scan QR code using the camera and save the captured frame."""
    cap = cv2.VideoCapture(0)
    print("Press 'q' to quit the camera.")

    qr_detector = cv2.QRCodeDetector()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to access the camera.")
            break

        data, points, _ = qr_detector.detectAndDecode(frame)
        if data:
            if points is not None:
                points = points[0].astype(int)  # Convert points to integers
                for i in range(len(points)):
                    next_point = points[(i + 1) % len(points)]
                    cv2.line(frame, tuple(points[i]), tuple(next_point), (0, 255, 0), 2)

            cv2.putText(frame, data, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            # Save the scanned frame for reference
            scanned_image_path = "scanned_qr_code.png"
            cv2.imwrite(scanned_image_path, frame)

            cap.release()
            cv2.destroyAllWindows()
            return data, scanned_image_path

        cv2.imshow("QR Code Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None, None

def decode_qr_code(image_path):
    """Decode a QR code from an image file."""
    img = cv2.imread(image_path)
    if img is not None:
        data, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
        return data
    return None

@app.post("/scan", response_class=HTMLResponse)
def scan():
    folder = 'Images'
    if not os.path.exists(folder):
        return f"""
        <html>
        <head>
            <title>QR Code Scanner - Error</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f9;
                    text-align: center;
                    padding: 50px;
                }}
                h1 {{
                    color: #d9534f;
                }}
                a {{
                    color: #007bff;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <h1>Error</h1>
            <p>Folder <b>{folder}</b> does not exist. Please provide a valid path.</p>
            <a href="/">Go Back</a>
        </body>
        </html>
        """

    print("Scanning for QR code using the camera...")
    scanned_qr_code, scanned_image_path = scan_qr_code_from_camera()

    if scanned_qr_code:
        print(f"Scanned QR Code Data: {scanned_qr_code}")

        verified = False
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)

            if not os.path.isfile(file_path):
                continue

            image_qr_data = decode_qr_code(file_path)
            if image_qr_data:
                print(f"Comparing with QR Code in {filename}: {image_qr_data}")

                if scanned_qr_code == image_qr_data:
                    print(f"Verified: QR code matches with {filename}.")
                    verified = True
                    return f"""
                    <html>
                    <head>
                        <title>QR Code Scanner - Verified</title>
                        <style>
                            body {{
                                font-family: Arial, sans-serif;
                                background-color: #f4f4f9;
                                text-align: center;
                                padding: 50px;
                            }}
                            h1 {{
                                color: #5cb85c;
                            }}
                            a {{
                                color: #007bff;
                                text-decoration: none;
                            }}
                            a:hover {{
                                text-decoration: underline;
                            }}
                        </style>
                    </head>
                    <body>
                        <h1>QR Code Verified</h1>
                        <p>QR code matches with <b>{filename}</b>.</p>
                        <br><br>
                        <a href="/">Go Back</a>
                    </body>
                    </html>
                    """

        if not verified:
            print("Not Verified: No matching QR code found in the folder.")
            return f"""
            <html>
            <head>
                <title>QR Code Scanner - Not Verified</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f9;
                        text-align: center;
                        padding: 50px;
                    }}
                    h1 {{
                        color: #d9534f;
                    }}
                    a {{
                        color: #007bff;
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                </style>
            </head>
            <body>
                <h1>QR Code Not Verified</h1>
                <p>No matching QR code found in the folder.</p>
                <br><br>
                <a href="/">Go Back</a>
            </body>
            </html>
            """
    else:
        print("No QR code detected. Please try again.")
        return """
        <html>
        <head>
            <title>QR Code Scanner - Error</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f9;
                    text-align: center;
                    padding: 50px;
                }
                h1 {
                    color: #d9534f;
                }
                a {
                    color: #007bff;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <h1>Error</h1>
            <p>No QR code detected. Please try again.</p>
            <a href="/">Go Back</a>
        </body>
        </html>
        """
