from pypdf import PdfReader
reader = PdfReader("EY_Digital_PDF_Practice.pdf")
print("Pages:", len(reader.pages))

whole_text =""
for page in reader.pages:
    whole_text += page.extract_text()
    print(whole_text)

print("=============================================================")

page = reader.pages[0]
page1 = page.extract_text()
print(page1)

print("=============================================================")
page = reader.pages[1]
page2 = page.extract_text()
print(page2)

print("=============================================================")
print(f"{page1}\n{page2}")

if "NorthStar Maintenance" in whole_text:
    print("NorthStar Maintenance is present")

count = 0
for sentence in whole_text.split("\n"):
    for word in sentence:
        if "vendor" in sentence:
            count +=1

print(count)

with open("pypdf_output.txt","w") as f:
    f.write(whole_text)
