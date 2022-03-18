#! /usr/bin/python3
import io
import time
import nfc
import argparse
from PIL import Image, ImageOps

TYPE_2_9_IN_TAG = 0x7
TYPE_4_2_IN_TAG = 0xA
TYPE_7_5_IN_TAG = 0xE

XFER_SUCCESS = bytes([0x0, 0x0])
REFRESH_TIMEOUT = 7


class WaveshareTagWriter:
    def __init__(self, tag_type: int) -> None:
        self.id = tag_type
        if tag_type == TYPE_2_9_IN_TAG:
            self.width = 128
            self.height = 296
            self.xfer_size_bytes = 16
        elif tag_type == TYPE_4_2_IN_TAG:
            self.width = 400
            self.height = 300
            self.xfer_size_bytes = 100
        elif tag_type == TYPE_7_5_IN_TAG:
            self.width = 800
            self.height = 480
            self.xfer_size_bytes = 120
        self._calculate_loops()

    def _calculate_loops(self) -> None:
        self.loops = int((self.width * self.height) / (self.xfer_size_bytes * 8))

    def _transceive(self, command_bytes: bytes, raise_fail: bool = True) -> bytes:
        resp = self.tag.transceive(command_bytes)
        if command_bytes[0] == bytes([0xcd]):
            if resp != XFER_SUCCESS and raise_fail:
                raise ValueError("Incompatable NFC Device Present")
        return resp

    def connect_and_check(self, tag: nfc.tag.Tag) -> None:
        self.tag = tag
        id = self._transceive(bytes([0x30, 0x00]))
        if id[0:7] != bytes("WSDZ10m", 'ascii') and id[0:7] != bytes("FSTN10m", 'ascii'):
            print(id[0:7])
            raise ValueError("Incompatable NFC Device Present")

    def setup(self) -> None:
        commands = [
            [0xcd, 0xd],
            [0xcd, 0x0, self.id],   # select type and reset e-paper
            [0xcd, 0x1],            # normal mode
            [0xcd, 0x2],            # config1
            [0xcd, 0x3],            # power on
            [0xcd, 0x5],            # config2
            [0xcd, 0x6],            # EDP load to main
            [0xcd, 0x7, 0x0],       # Data preparation
        ]
        for command in commands:
            self._transceive(bytes(command))

    def transmit_image(self) -> None:
        line_prefix = bytes([0xcd, 0x8, self.xfer_size_bytes])
        # TODO: to support multicolor images, channels are sent separately
        # red channel line_prefix would be [0xcd, 0x19, self.xfer_size_bytes]
        # I don't have a multi-color tag to test
        for i in range(self.loops):
            start = i * self.xfer_size_bytes
            end = i * self.xfer_size_bytes + self.xfer_size_bytes
            data = self.img_bytes[start:end]
            self._transceive(bytes(line_prefix + data))
            print(f"Uploading in Progress: {i}/{self.loops} -- {100 * i / self.loops:.{1}f}%", end="\r")
        print("Upload complete")

    def finish(self) -> None:
        commands = [
            [0xcd, 0x18],   # power on
            [0xcd, 0x9],    # refresh
        ]
        for command in commands:
            self._transceive(bytes(command))

        start_time = time.time()

        # wait for ready
        print("Refreshing...")
        while(True):
            resp = self._transceive(bytes([0xcd, 0xa]), raise_fail=False)
            if resp == bytes([0xFF, 0x0]):
                break
            time.sleep(0.1)
            if time.time() > start_time + REFRESH_TIMEOUT:
                print("Timeout exceeded!")
                raise TimeoutError

        # power off
        self._transceive(bytes([0xcd, 0x4]))
        time.sleep(0.5)  # Keep tag powered, finish writing tag

    def load_image(self, image_path: str) -> None:
        im = Image.open(image_path)
        im = ImageOps.invert(im.convert('L'))
        im = im.convert('1')
        if im.width == self.height and im.height == self.width:  # we need to rotate image
            im = im.transpose(Image.ROTATE_90)
        elif im.width == self.width and im.height == self.height:
            pass
        else:
            raise ValueError("Invalid Image Size")
        arr = io.BytesIO()
        im.save(arr, format='PPM')
        self.img_bytes = arr.getvalue()[11:]  # Remove PBM image header

    def set_image(self, im: Image):
        im = ImageOps.invert(im.convert('L'))
        im = im.convert('1')
        if im.width == self.height and im.height == self.width:  # we need to rotate image
            im = im.transpose(Image.ROTATE_90)
        elif im.width == self.width and im.height == self.height:
            pass
        else:
            raise ValueError("Invalid Image Size")
        arr = io.BytesIO()
        im.save(arr, format='PPM')
        self.img_bytes = arr.getvalue()[11:]

    def connected(self, tag: nfc.tag.Tag) -> None:
        self.connect_and_check(tag)
        self.setup()
        self.transmit_image()
        self.finish()


def float_to_tag_model(tag_float: float) -> int:
    if tag_float == 2.9:
        return TYPE_2_9_IN_TAG
    elif tag_float == 4.2:
        return TYPE_4_2_IN_TAG
    elif tag_float == 7.5:
        return TYPE_7_5_IN_TAG
    else:
        raise ValueError("Please select a valid tag size")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Write image to Waveshare e-paper tag")
    ap.add_argument("tag_type", type=float, help="2.9, 4.2, 7.5")
    ap.add_argument("filename", type=str, help="path to image file of correct size")
    args = ap.parse_args()
    writer = WaveshareTagWriter(float_to_tag_model(args.tag_type))
    writer.load_image(args.filename)

    clf = nfc.ContactlessFrontend('usb')
    clf.connect(rdwr={'on-connect': writer.connected})
    clf.close()
