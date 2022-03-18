# Waveshare NFC Tag writer
Inspired by [wne_writer](https://gitlab.com/bettse/wne_writer)

## Usage:
### label_maker

`python3 label_maker.py 4.2 https://www.google.com "Title" "This is a description"`

```
usage: label_maker.py [-h] tag_type url title description

Write image to Waveshare e-paper tag

positional arguments:
  tag_type     2.9, 4.2, 7.5
  url          URL to write to tag
  title        Title to write to tag
  description  Description to write to tag

optional arguments:
  -h, --help   show this help message and exit
```

### qrcode2tag

`python3 qrcode2tag.py 4.2 https://fancyurl.example.com`


```
usage: qrcode2tag.py [-h] tag_type url

Write image to Waveshare e-paper tag

positional arguments:
  tag_type    2.9, 4.2, 7.5
  url         URL to write to tag

optional arguments:
  -h, --help  show this help message and exit
```


### wavershare_tag_writer

`python3 wavershare_tag_writer.py 4.2 /path/to/image/of/correct/size.png`


```
usage: waveshare_tag_writer.py [-h] tag_type filename

Write image to Waveshare e-paper tag

positional arguments:
  tag_type    2.9, 4.2, 7.5
  filename    path to image file of correct size

optional arguments:
  -h, --help  show this help message and exit
```
