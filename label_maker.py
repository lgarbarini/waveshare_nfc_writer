#! /usr/bin/python3
import argparse
import nfc
from qrcode2tag import new_qr_code
from PIL import Image, ImageFont, ImageDraw
from waveshare_tag_writer import WaveshareTagWriter, float_to_tag_model


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Write image to Waveshare e-paper tag")
    ap.add_argument("tag_type", type=float, help="2.9, 4.2, 7.5")
    ap.add_argument("url", type=str, help="URL to write to tag")
    ap.add_argument("title", type=str, help="Title to write to tag")
    ap.add_argument("description", type=str, help="Description to write to tag")
    args = ap.parse_args()

    writer = WaveshareTagWriter(float_to_tag_model(args.tag_type))
    qr_img = new_qr_code(args.url, writer.width, writer.height, pad=False)
    img = Image.new("1", (writer.width, writer.height), 'white')
    draw = ImageDraw.Draw(img)
    # futura = ImageFont.truetype("fonts/futura_medium.ttf", 20)
    # futura_bold = ImageFont.truetype("fonts/futura_bold.ttf", 70)
    draw.text((10, 0), f"{args.title}")  # , font=futura_bold)
    line = args.description.replace("\\n", "\n")
    draw.text((10, 75), f"{line}")  # , font=futura)
    img.paste(qr_img, (writer.width - qr_img.height, writer.height - qr_img.height))

    writer.set_image(img)

    clf = nfc.ContactlessFrontend('usb')
    clf.connect(rdwr={'on-connect': writer.connected})
    clf.close()
