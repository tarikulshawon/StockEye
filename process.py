import pdfplumber
import pandas as pd
import os
import matplotlib.pyplot as plt
from tkinter import *
from bdshare import get_current_trade_data
import GUI as gui

def open_all_pdfs(directory):
    # List all files in the directory
    files = os.listdir(directory)

    # Filter to include only PDF files
    pdf_files = [file for file in files if file.endswith('.pdf')]
    
    # Loop through all PDF files
    buy = []
    sale = []
    for pdf_file in pdf_files:
        pdf_path = os.path.join(directory, pdf_file)
        # Open the PDF file
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]  # Access the first page
            text = first_page.extract_text()

            # find date
            start_idx = text.find('Printed On:') # Start of the Buy section
            end_idx = text.find('Page')  # End just before the Total Buy summary
            relevant_text = text[start_idx:end_idx]
            date = relevant_text.split(' ')[2]
            #print(date)
            
            buy = buy + process_buy(text, date)
            sale = sale + process_sale(text, date)

    df_buy = pd.DataFrame(buy, columns=['Date', 'Name', 'Units', 'Rate', 'Total Price'])
    df_sale = pd.DataFrame(sale, columns=['Date', 'Name', 'Units', 'Rate', 'Total Price'])
    #print(df_buy)
    #print(df_sale)
    return df_buy, df_sale

def process_buy(text, date):
    start_idx = text.find('Buy') # Start of the Buy section
    end_idx = text.find('TOTAL BUY:')  # End just before the Total Buy summary

    relevant_text = text[start_idx:end_idx]
    lines = relevant_text.split('\n')
    lines = lines[1:-1]
    #print(lines)
    data = []
    for line in lines:
            parts = line.split(" ")
            instrument = parts[0]
            quantity = int(parts[1])
            price = round(float(parts[2]), 2)
            total_price = round(float(parts[5].replace(',', '')), 2)
            data.append([date, instrument, quantity, price, total_price])

    return data

def process_sale(text, date):
    start_idx = text.find('Sale') # Start of the Buy section
    end_idx = text.find('TOTAL SALE:')  # End just before the Total Buy summary

    relevant_text = text[start_idx:end_idx]
    lines = relevant_text.split('\n')
    lines = lines[1:-1]
    #print(lines)
    data = []
    for line in lines:
            parts = line.split(" ")
            instrument = parts[0]
            quantity = int(parts[1])
            price = round(float(parts[2]), 2)
            total_price = round(float(parts[5].replace(',', '')), 2)
            data.append([date, instrument, quantity, price, total_price])

    return data


def getInformation(name, buy, sale):    
    bb = buy[buy['Name'] == name].sort_values('Rate')
    ss = sale[sale['Name'] == name].sort_values('Rate')
    print("..........           BUY           ...........")
    print(bb)
    print("\n..........        SALE           ...........")
    print(ss)
    
    itemNames = buy['Name'].unique()
    gui.showTable(buy, sale, name=name)


buy, sale = open_all_pdfs("reports")

print(buy['Name'].unique())
getInformation(buy['Name'][0], buy, sale)
