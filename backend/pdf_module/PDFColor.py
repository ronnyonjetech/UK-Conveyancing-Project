import fitz  # PyMuPDF

class PDFHighlighter:
    def __init__(self, input_pdf_path, output_pdf_path):
        self.input_pdf_path = input_pdf_path
        self.output_pdf_path = output_pdf_path
        self.pdf_document = fitz.open(input_pdf_path)

    def highlight_text(self, text_list):
        # Iterate through each page of the PDF
        for page_num in range(len(self.pdf_document)):
            page = self.pdf_document[page_num]

            # Iterate through each text string to highlight
            for text_to_highlight in text_list:
                # Search for the text to highlight in the page's text
                text_instances = page.search_for(text_to_highlight)

                # Iterate through each text instance and highlight it
                for inst in text_instances:
                    # Define the highlight annotation rectangle
                    rect = fitz.Rect(inst)

                    # Add a highlight annotation to the page
                    highlight = page.add_highlight_annot(rect)

                    # Set the color of the highlight (yellow) and opacity
                    highlight.set_colors({"stroke": (1, 1, 0), "fill": (1, 1, 0), "alpha": 0.4})
        
    def save_highlighted_pdf(self):
        # Save the modified PDF to the output file
        self.pdf_document.save(self.output_pdf_path)
        return self.pdf_document
    
    def close_document(self):
        # Close the PDF document
        try:
            self.pdf_document.close()
        except Exception as e:
            print(f"Error : {e}")
