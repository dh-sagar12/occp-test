import qrcode

def generate_qr(device_id: str):
    # URL format: /connect?device_id={device_id}&user_id={user_id}&vehicle_id={vehicle_id}
    base_url = "localhost:8000/api/v1/connect"
    url = f"{base_url}?device_id={device_id}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    img.save(f"device_{device_id}_qr.png")

# Example usage:
generate_qr("device123")
