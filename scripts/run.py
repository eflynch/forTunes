
import os
from music21 import converter
from PyPDF2 import PdfReader, PdfWriter

major_keys = [
    'Cb', 'Gb', 'Db', 'Ab', 'Eb', 'Bb', 'F', 'C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#'
]
minor_keys = [
    'Ab', 'Eb', 'Bb', 'F', 'C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#'
]
modes = ["min", "maj", "dor", "phr", "lyd", "mix", "loc"]
def key_to_keywords(key):
    key = key.lower()
    for mode in modes:
        if mode in key:
            root = key[:key.find(mode)]
            break
    minor = ["min", "dor", "phr", "loc"].count(mode) > 0
    keymi = 1 if minor else 0 
    roots = minor_keys if minor else major_keys
    index = roots.index(root.title())
    keysf = index - 7
    return [f"keysf:{keysf}", f"keymi:{keymi}",]


def abc_to_pdf(input_txt_file, genre=None):
    output_pdf_file = input_txt_file.replace('.txt', '.pdf')
    # Read the ABC notation from the input text file
    with open(input_txt_file, 'r') as file:
        abc_notation = file.read()

    # Convert the ABC notation to a music21 stream
    score = converter.parse(abc_notation, format='abc')

    forms = []
    keys = []
    for line in abc_notation.splitlines():
        if line.startswith('R:'):
            forms.append(line[2:].rstrip().lstrip().title())
        elif line.startswith('K:'):
            keys.append(line[2:].rstrip().lstrip())

    keywords = forms + key_to_keywords(keys[0])

    temp_pdf_file = 'temp_score.pdf'
    score.write('musicxml.pdf', fp=temp_pdf_file)

    # Read the temporary PDF file
    pdf_reader = PdfReader(temp_pdf_file)
    pdf_writer = PdfWriter()
    pdf_writer.append_pages_from_reader(pdf_reader)

    composers = (score.metadata.composer or "Unknown").split(" and ")

    # Add metadata
    metadata = {
        '/Title': score.metadata.title or "Music Score",
        '/Author': ", ".join(composers), 
        '/Subject': (genre or "Unknown").title(),
        '/Keywords': ", ".join(keywords)
    }
    pdf_writer.add_metadata(metadata)

    # Write the final PDF file with metadata
    with open(output_pdf_file, 'wb') as output_file:
        pdf_writer.write(output_file)
    
    # Delete the temporary PDF file and others
    os.remove(temp_pdf_file)
    os.remove('temp_score.musicxml')


if __name__ == "__main__":
    for root, dirs, files in os.walk('abc'):
        folder = root.split(os.sep)[-1]
        for file in files:
            if file.endswith('.txt'):
                input_txt_file = os.path.join(root, file)
                abc_to_pdf(input_txt_file, genre=folder)