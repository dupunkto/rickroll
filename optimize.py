#!/usr/bin/env python3

import os
import re
import base64
import hashlib

from urllib.parse import urlparse
from bs4 import BeautifulSoup

in_path = 'source.html'
out_path = 'index.html'
out_dir = 'optimized'

os.makedirs(out_dir, exist_ok=True)

def save_data_uri_as_image(data_uri, image_format):
    ext = "svg" if image_format == "svg+xml" else image_format
    data = data_uri.split(",")[1]  # Get the base64 part
    img_data = base64.b64decode(data)
    
    file_hash = hashlib.md5(data.encode('utf-8')).hexdigest()
    filename = f"image_{file_hash[:8]}.{ext}"
    image_path = os.path.join(out_dir, filename)
    
    with open(image_path, 'wb') as img_file:
        img_file.write(img_data)
    
    return filename

def save_font_data_uri_as_url(font_data_uri, comment_url):
    # Return the URL from the comment (we assume the comment is always well-formed)
    return comment_url.strip("/*savepage-url=").strip("*/")

def process_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    img_tags = soup.find_all('img', src=re.compile('^data:image/'))
    for img_tag in img_tags:
        data_uri = img_tag['src']
        image_format = data_uri.split(';')[0].split('/')[1]
        image_filename = save_data_uri_as_image(data_uri, image_format)
        img_tag['src'] = os.path.join(out_dir, image_filename)
    
    css_content = ""
    style_tags = soup.find_all('style')
    for style_tag in style_tags:
        css_content += style_tag.get_text() + "\n"
        style_tag.decompose()  # Remove the style tag from HTML
    
    css_content = re.sub(
        r'url\((data:font/woff2;base64,.*?)(/\*savepage-url=.*?\*/)\)', 
        lambda m: f"url({save_font_data_uri_as_url(m.group(1), m.group(2))})", 
        css_content
    )

    if css_content:
        css_filename = 'styles.css'
        css_file_path = os.path.join(out_dir, css_filename)
        with open(css_file_path, 'w') as css_file:
            css_file.write(css_content)

        new_link_tag = soup.new_tag('link', rel='stylesheet', href=css_file_path)
        soup.head.append(new_link_tag)

    return str(soup)

def main():
    with open(in_path, 'r', encoding='utf-8') as file:
        html = file.read()

    optimized = process_html(html)

    with open(out_path, 'w', encoding='utf-8') as file:
        file.write(optimized)

    print(f"Optimized HTML saved to: {out_path}")
    print(f"Images saved to: {out_dir}")
    print(f"CSS extracted to: {os.path.join(out_dir, 'styles.css')}")

if __name__ == '__main__':
    main()
