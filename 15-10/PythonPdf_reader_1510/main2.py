import pymupdf
import pytesseract
from PIL import Image
doc = pymupdf.open("EY_Scanned_PDF_OCR_Practice.pdf")

ocr_text = ""
for page in doc:
    pix = page.get_pixmap()
    pix.save("temp.png")

    image = Image.open("temp.png")
    text = pytesseract.image_to_string(image)

    ocr_text += text + "\n"

print("================================================================")

page = doc[0]
pix = page.get_pixmap()
pix.save("scanned_page.png")
image = Image.open("scanned_page.png")
text = pytesseract.image_to_string(image)
print(text)

print("================================================================")


if "Forklift FL-17" in ocr_text:
    print("Forklift FL-17 is present")
if "injuries" in ocr_text:
    print("Injuries are present")

sentences = ocr_text.split(".")
for sentence in sentences:
    if "inspection" in sentence.lower():
        print(sentence.strip())


with open("ocr_result.txt","w") as f:
    f.write(ocr_text)

count = 0
for sentence in sentences:
    if "inspection" in sentence.lower():
        count += 1

print(count)

for sentence in sentences:
    if "Loading Bay" in sentence:
        print(sentence)



