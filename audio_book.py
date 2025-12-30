import pyttsx3
from PyPDF2 import PdfReader
from tkinter.filedialog import askopenfilename

book_path = askopenfilename()

# OPEN THE FILE PROPERLY (IMPORTANT!)
with open(book_path, "rb") as book:
    pdf_reader = PdfReader(book)
    speaker = pyttsx3.init()

    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            speaker.say(text)

    speaker.runAndWait()
    speaker.stop()

