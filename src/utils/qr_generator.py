import qrcode
import json

# Define the charge point data
charge_point_data = {
    "chargePointId": 1,
    "name": "Charge Point 1",
    "location": "Garage 1",
    "status": "Available"
}

# Convert the data to JSON
data_json = json.dumps(charge_point_data)

# Generate the QR code
qr = qrcode.QRCode(
    version=1,  # controls the size of the QR code
    error_correction=qrcode.constants.ERROR_CORRECT_L,  # error correction level
    box_size=10,  # size of the boxes in the QR code grid
    border=4,  # thickness of the border (in boxes)
)
qr.add_data(data_json)
qr.make(fit=True)

# Create an image from the QR code
img = qr.make_image(fill='black', back_color='white')

# Save the QR code as an image file
img.save("charge_point_qr.png")

print("QR code generated and saved as 'charge_point_qr.png'")
