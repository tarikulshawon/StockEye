from bdshare import get_current_trade_data
import customtkinter
from CTkTable import *
from tkinter import *


# df = get_current_trade_data('GP') # get specific instrument data
# print(df.to_string())

def calculateGain(bb, ss):
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
    print(f"Realised Gain: {gain}")
    return gain

def showTable(bb, ss, name):
    root = customtkinter.CTk()
    
    buy = bb[bb['Name'] == name].sort_values('Rate')
    sale = ss[ss['Name'] == name].sort_values('Rate')
    
    profit = calculateGain(buy, sale)
    title = f"{name} (Realized gain: {profit})"
    root.title(title)
    
    value = [buy.columns]
    count = int(buy['Date'].count())
    
    for id in range(0, count):
        value.append(buy.iloc[id])
    
    # calculate avg rate
    value.append(["", "", "Avg", round(buy['Total Price'].sum() / buy['Units'].sum(), 2), ""])

    buy_table = CTkTable(master=root, row=count+2, column=5, values=value)
    buy_table.pack(expand=True, fill="both", padx=20, pady=20)
    
    value = [sale.columns]
    count = int(sale['Date'].count())

    for id in range(0, count):
        value.append(sale.iloc[id])
        
    # calculate avg rate
    value.append(["", "", "Avg", round(sale['Total Price'].sum() / sale['Units'].sum(), 2), ""])
        
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

    sale_table = CTkTable(master=root, row=count+2, column=5, values=value)
    sale_table.pack(expand=True, fill="both", padx=20, pady=20)
    root.mainloop()