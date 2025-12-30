from PIL import Image
img = Image.open("rna_icon.png")
img.save("rna_icon.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
print("Icon created successfully.")
