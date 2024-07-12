from django.shortcuts import render
from django.http import JsonResponse
from userAccount.serializers import PdfSerializer,AnalyzedSerializer
from .models import Conveyance,AnalyzedConveyance
# Create your views here.
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
import time
import os
import fitz 
import re
import nltk     
import heapq 
from django.core.files import File
from django.core.files.base import ContentFile
import io
import logging
import os
from PIL import Image
from io import BytesIO
import numpy as np
from django.shortcuts import get_object_or_404
#uploads\IRRIGATION_Letter_OdJDaBr.pdf
file_path=''

# def pdfConversion(file_path):
#     print(file_path)
#     file_path=re.sub("^/|/$", "", file_path)
#     doc = fitz.open(file_path) 
#     text = "" 
#     for page in doc: 
#       text=text+page.get_text() 
#     # text=''.join(text.split())
#     # print(text)
#     return text

# Initialize EasyOCR reader
#reader = easyocr.Reader(['en'])  # You can add more languages if needed

def pdfConversion(file_path):
    # Print file path for debugging
    print(file_path)
    
    # Remove leading and trailing slashes from file path
    file_path = re.sub("^/|/$", "", file_path)
    
    # Open the PDF file
    doc = fitz.open(file_path)
    text = ""
    
    # Iterate through each page
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_text = page.get_text()
        
        # If no text found, use OCR
        if not page_text.strip():
            # pix = page.get_pixmap()
            # img = Image.open(BytesIO(pix.tobytes()))
            # results = reader.readtext(np.array(img))
            # ocr_text = " ".join([result[1] for result in results])
            # text += ocr_text
            text="The document contains OCR and Layout"
        else:
            text += page_text

    
    return text


def textSummarizer(text):
    nltk.download('punkt')
    nltk.download('stopwords')
    #Removing Square brackets and Extra spaces
    text=re.sub(r'\[[0-9]*\]',' ',text)
    text=re.sub(r'\s+',' ',text)
    text=text.lower()
    #Removing special characters and digits and lowering
    format_text=re.sub('[^a-zA-Z]',' ',text)
    format_text=re.sub(r'\s+',' ',format_text)
    format_text.lower()

    sentence_list=nltk.sent_tokenize(text)
    stopwords=nltk.corpus.stopwords.words('english')

    word_frequencies = {}
    for word in nltk.word_tokenize(format_text):
        if word not in stopwords:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1
        maximum_frequncy = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)
        sentence_scores = {}
    for sent in sentence_list:
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if len(sent.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]
    
    summary_sentences = heapq.nlargest(9, sentence_scores, key=sentence_scores.get)

    summary = ' '.join(summary_sentences)
    print(summary)
    return summary

def highlight_text_in_pdf(text_list, input_pdf_path):
    # Open the input PDF file
    pdf_document = fitz.open(input_pdf_path)

    # Iterate through each page of the PDF
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]

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

    # Save the modified PDF to the output file

    # pdf_document.save(output_pdf_path)
    # print(type(output_pdf_path))

    # Close the PDF document
    
     # Create an in-memory byte stream to hold the PDF data
    pdf_bytes_stream = io.BytesIO()

    # Write the PDF document to the byte stream
    pdf_document.save(pdf_bytes_stream)

    # Get the byte data from the byte stream
    pdf_bytes = pdf_bytes_stream.getvalue()

    print(type(pdf_bytes))
    pdf_document.close()

    return pdf_bytes


@api_view(['GET'])
def pdf_files(request):
    pdf_files=Conveyance.objects.all()
    serializer=PdfSerializer(pdf_files,many=True)
    #pdfConversion(file_path)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAnalyzedPdf(request):
   # Retrieve the authenticated user's ID
    authenticated_user_id = request.user.id
    pdf_files = AnalyzedConveyance.objects.filter(conveyance__user_id=authenticated_user_id)
    serializer=AnalyzedSerializer(pdf_files,many=True)
    # print(serializer.data)
    return Response(serializer.data)

@api_view(['GET'])
def analyzed_conveyance_detail(request, pk):
    # Retrieve the AnalyzedConveyance object based on the primary key (pk)
    analyzed_conveyance = get_object_or_404(AnalyzedConveyance, pk=pk)
    # Serialize the AnalyzedConveyance object
    serializer = AnalyzedSerializer(analyzed_conveyance)
    # Return serialized data as response
    return Response(serializer.data)

@api_view(['GET'])
def get_pdf(request,pk):
    pdf_files=Conveyance.objects.get(id=pk)
    serializer=PdfSerializer(pdf_files,many=False)
    return Response(serializer.data)

@api_view(['POST'])
def post_pdf(request):
    serializer=PdfSerializer(data=request.data)
    if serializer.is_valid():
        #print(type(serializer.validated_data))
        d=serializer.validated_data
        serializer.save()
        #print(d['file'])
        #time.sleep(5)
        print(serializer.data)
        y=serializer.data
        
       # print(y["id"])
        extracted_text=pdfConversion (y["file"])
        #summarizer = pipeline ("summarization", model="facebook/bart-large-cnn")
        # print(summarizer(extracted_text, max_length=244, min_length=30, do_sample=False))
        #summary=summarizer(extracted_text, max_length=244, min_length=30, do_sample=False)
        # print(type(extracted_text))
        summary=textSummarizer(extracted_text)
        file_path=y["file"]
        file_path=re.sub("^/|/$", "", file_path)
        # Open the PDF file in binary mode for reading
        with open(file_path, 'rb') as pdf_file:
            
            ex=nltk.sent_tokenize(summary)
            # Read the file content
            pdf_content = pdf_file.read()
        
            print(type(pdf_content))
            
            pdf_bytes=highlight_text_in_pdf(ex,file_path)
            pdf_content=pdf_bytes
            analyzed_instance = AnalyzedConveyance()

            # Set attributes of the instance
            #analyzed_instance.user=y["user"]
            analyzed_instance.conveyance_id=y["id"]
            analyzed_instance.extracted_text=extracted_text
            analyzed_instance.summarized_text=summary
           
             
            # Create a ContentFile with the PDF content and specify the filename
            pdf_content_file = ContentFile(pdf_content, name=os.path.basename(file_path))

            # Set the 'pdf_file' field with the ContentFile
            analyzed_instance.analyzed_file.save(os.path.basename(file_path), pdf_content_file, save=True)

            # Save the model instance to the database
            analyzed_instance.save()
       

        # analyzed_instance=AnalyzedConveyance()
        # analyzed_instance.conveyance_id=y["id"]
        # analyzed_instance.extracted_text=extracted_text
        # analyzed_instance.summarized_text=summary
        # analyzed_instance.analyzed_file=y["file"]
        # file_path=y["file"]
        # file_path=re.sub("^/|/$", "", file_path)
        # analyzed_instance.analyzed_file.save(y["file_name"], File(open(file_path, 'rb')))
        # analyzed_instance.save()
        # AnalyzedConveyance.objects.create(conveyance_id=y["id"], extracted_text= extracted_text,summarized_text=summary,analyzed_file=y["file"])
        return Response(serializer.data,status=status.HTTP_201_CREATED)
        
    # print(serializer.data.file)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


