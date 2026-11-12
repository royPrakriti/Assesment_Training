import pymupdf

pdf = pymupdf.open("EY_Digital_PDF_Practice.pdf")

print(pdf.page_count)

print("========================================================================")

page1 = pdf[0]
print(page1.get_text())

print("========================================================================")

all_text_from_the_file = ""

for page in pdf:
    all_text_from_the_file += page.get_text()

print(all_text_from_the_file)

print("========================================================================")


if "Maintenance" in all_text_from_the_file:
    print("Maintenance is present")

print("========================================================================")

count = 0
if "V303" in all_text_from_the_file:
    count += 1

print(count)

print("========================================================================")
page2 = pdf[1]
print(page2.get_text())

with open("digital_pdf_text.txt", "w") as file:
    file.write(all_text_from_the_file)




pdf.close()
