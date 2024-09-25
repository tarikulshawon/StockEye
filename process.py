import pdfplumber
import pandas as pd
import os
import matplotlib.pyplot as plt
import customtkinter
from CTkTable import *
from tkinter import *

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
            price = float(parts[2])
            total_price = float(parts[5].replace(',', ''))
            data.append([date, instrument, quantity, price, total_price])

    # Create DataFrame
    df = pd.DataFrame(data, columns=['Date', 'Instrument Name', 'Total Qty.', 'Avg. Rate(TK.)', 'Total Price'])
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
            price = float(parts[2])
            total_price = float(parts[5].replace(',', ''))
            data.append([date, instrument, quantity, price, total_price])

    # Create DataFrame
    df = pd.DataFrame(data, columns=['Date', 'Instrument Name', 'Total Qty.', 'Avg. Rate(TK.)', 'Total Price'])
    return data

def showTable(bb, ss, name):
    root = customtkinter.CTk()
    root.title('Buy/Sale')
    
    buy = bb[bb['Name'] == name].sort_values('Rate')
    sale = ss[ss['Name'] == name].sort_values('Rate')
    
    value = [buy.columns]
    count = int(buy['Date'].count())
    
    for id in range(0, count):
        value.append(buy.iloc[id])

    buy_table = CTkTable(master=root, row=count+1, column=5, values=value)
    buy_table.pack(expand=True, fill="both", padx=20, pady=20)
    
    value = [sale.columns]
    count = int(sale['Date'].count())

    for id in range(0, count):
        value.append(sale.iloc[id])
        
    variable = StringVar(root)
    variable.set("Select") # default value

    def execute():
        selected_name = variable.get()
        print ("value is:" + selected_name)
        showTable(bb, ss, selected_name)

    button = Button(root, text="Run", command=execute, width=10, default="disabled")
    button.pack()

    list = bb['Name'].unique()
    w = OptionMenu(root, variable, *list)
    w.pack()

    sale_table = CTkTable(master=root, row=count+1, column=5, values=value)
    sale_table.pack(expand=True, fill="both", padx=20, pady=20)
    root.mainloop()

def getInformation(name, buy, sale):    
    bb = buy[buy['Name'] == name].sort_values('Rate')
    ss = sale[sale['Name'] == name].sort_values('Rate')
    print("..........           BUY           ...........")
    print(bb)
    print("\n..........        SALE           ...........")
    print(ss)
    
    itemNames = buy['Name'].unique()
    showTable(buy, sale, name=name)

    # realised gain
    total_buy = 0.0
    total_sale = ss['Total Price'].sum()
    total_unit = ss['Units'].sum()
    
    for idx in bb.index:
        if total_unit >= int(bb['Units'][idx]):
            total_unit = total_unit - int(bb['Units'][idx])
            total_buy = total_buy + bb['Total Price'][idx]
        elif total_unit < int(bb['Units'][idx]):
            total_buy = total_buy + total_unit * bb['Rate'][idx]
            total_unit = 0
            
        if total_unit == 0:
            break    
    gain = total_sale - total_buy
    print(f"gain: {gain}")

buy, sale = open_all_pdfs("reports")

print(buy['Name'].unique())
getInformation('SONALIANSH', buy, sale)
