#! /usr/bin/python3
import qrcode
import argparse
import nfc
from PIL import Image
from waveshare_tag_writer import WaveshareTagWriter, float_to_tag_model


def new_qr_code(url, width, height, resize=True, pad=True) -> Image:
    qr = qrcode.QRCode(version=1, box_size=1, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    if resize:
        scale_x = width / img.width
        scale_y = height / img.height
        if scale_x > 2 and scale_y > 2:
            if scale_x > scale_y:
                scale_factor = int(scale_y)
                img = img.resize((img.width * scale_factor, img.width * scale_factor))
            elif scale_y > scale_x:
                scale_factor = int(scale_x)
                img = img.resize((img.width * scale_factor, img.width * scale_factor))
        elif scale_x < 1 or scale_y < 1:
            print("Scaling down")
            if scale_x > scale_y:
                scale_factor = int(scale_x)
                img = img.resize((img.width * scale_factor, img.width * scale_factor))
            elif scale_y > scale_x:
                scale_factor = int(scale_y)
                img = img.resize((img.width * scale_factor, img.width * scale_factor))

        if pad:
            left = width // 2 - img.width // 2
            right = left + img.width
            top = 20
            bottom = top + img.height
            padded = Image.new(img.mode, (width, height), 'white')
            padded.paste(img, (left, top, right, bottom))
            img = padded
    return img


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Write image to Waveshare e-paper tag")
    ap.add_argument("tag_type", type=float, help="2.9, 4.2, 7.5")
    ap.add_argument("url", type=str, help="URL to write to tag")
    args = ap.parse_args()

    writer = WaveshareTagWriter(float_to_tag_model(args.tag_type))
    img = new_qr_code(args.url, writer.width, writer.height)
    writer.set_image(img)

    clf = nfc.ContactlessFrontend('usb')
    clf.connect(rdwr={'on-connect': writer.connected})
    clf.close()
