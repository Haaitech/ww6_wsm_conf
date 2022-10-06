from turtle import color
from bs4 import BeautifulSoup
from tkinter import *
from tkinter import ttk, filedialog

WW6_FILE_PATH = None
WSM_FILE_PATH = None

Bs_wsm_data = None

def saveAs():
    global Bs_wsm_data
    global WSM_FILE_NAME

    print(str(WSM_FILE_NAME))

    f = filedialog.asksaveasfile(mode='w', defaultextension=".wsm")
    if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    text2save = Bs_wsm_data.prettify()
    f.write(text2save)
    f.close()

def open_ww6():
    global WW6_FILE_PATH
    global WW6_FILE_NAME
    global FILE_CONVERTED_TEXT

    WW6_FILE_PATH = (filedialog.askopenfilename(filetypes=(('wireless workbench 6', "*.shw"),)))
    WW6_FILE_NAME.set(WW6_FILE_PATH.split('/')[-1])

    FILE_CONVERTED_TEXT.set('')



def open_wsm():
    global WSM_FILE_PATH
    global WSM_FILE_NAME
    global FILE_CONVERTED_TEXT

    WSM_FILE_PATH = filedialog.askopenfilename(filetypes=(('WSM file', "*.wsm"),))
    WSM_FILE_NAME.set(WSM_FILE_PATH.split('/')[-1])

    FILE_CONVERTED_TEXT.set('')

def convertFile():
    
    global Bs_wsm_data

    #   Variables for creating specific structures so assigning data becomes easyer
    ww6_freq_plot = []

    #   A list of freq names to assign to wsm receivers ranges to cross refrence to the ww6 file
    senn_freq_ranges = {
        "470100-558000":"aw+",
        "558000-626000":"gw",
        "606000-678000":"gbw",
        "626000-668000":"b"
    }

    #   Open and assign to variable both the ww6 and wsm file
    with open(WW6_FILE_PATH, 'r') as ww6_file:
        ww6_data = ww6_file.read()

    with open(WSM_FILE_PATH, 'r') as wsm_file:
        wsm_data = wsm_file.read()

    #   Create Bs4 objects from the read data
    Bs_ww6_data = BeautifulSoup(ww6_data, 'xml')
    Bs_wsm_data = BeautifulSoup(wsm_data, 'xml')

    #   Assign all instances of a freq entry found in the ww6 file to an array
    freq_entry = Bs_ww6_data.find_all('freq_entry')

    #   Assing all instances of a receiver found in the wsm file to an array
    receicers = Bs_wsm_data.find_all('Receiver')


    #   For each freq entry found in the ww6 file extract the frequency value and the name of the freq band
    #   and then add those as an sub array to the ww6_freq_plot array
    for item in freq_entry:
        value = item.find('value').contents
        band = item.find('band').contents

        freq_combie = [band[0].lower(), value[0], True]

        ww6_freq_plot.append(freq_combie)


    #   for each instance of an receiver object found in the wsm file extract: lower freq limit, upper freq limit,
    #   current frequency and uniqe id. assign a band name according to the upper and lower freq limit
    #   loop through each freq in the ww6_freq_plot array and if the band name corresponds with the assignd
    #   band name and the is free value equals True assign the frequency as new_freq, then break out of the loop and continue with the next receiver.
    #   do this for each receiver and when done write to a new .wsm file.  
    for item in receicers:
        lower_freq_limit = item.find('LowerFrequencyLimit').contents[0]
        uper_freq_limit = item.find('UpperFrequencyLimit').contents[0]
        current_frequency = item.find('CurrentFrequency')
        uniqe_id = item.get('UniqueId')

        freq_range = lower_freq_limit + '-' + uper_freq_limit
        senn_freq_name = senn_freq_ranges[freq_range]
        new_freq = 0

        for freq in ww6_freq_plot:
            if freq[0] == senn_freq_name and freq[2] == True:
                new_freq = freq[1]
                freq[2] = False
                break
            else:
                continue

        current_frequency.string = new_freq
    
    FILE_CONVERTED_TEXT.set('Sucsessfully converted file!')
    


#  Tkinter setup
root = Tk()
root.title('WW6 freq plot to WSM')

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

style = ttk.Style(root)
#style.theme_use("clam")


style.map("C.TButton",
    foreground=[('pressed', 'green'), ('active', 'grey')],
    background=[('pressed', '!disabled', 'black'), ('active', 'white')]
    )

WW6_FILE_NAME = StringVar()
WSM_FILE_NAME = StringVar()
FILE_CONVERTED_TEXT = StringVar()


ttk.Button(mainframe, text="ww6 file", command=open_ww6, style='C.TButton').grid(column=1, row=2)
ttk.Label(mainframe, text="WW6 file: ").grid(column=1, row=3)
ttk.Label(mainframe, textvariable=WW6_FILE_NAME).grid(column=1, row=4)
ttk.Button(mainframe, text="wsm file", command=open_wsm, style='C.TButton').grid(column=3, row=2)
ttk.Label(mainframe, text="WSM file: ").grid(column=3, row=3)
ttk.Label(mainframe, textvariable=WSM_FILE_NAME).grid(column=3, row=4)


ttk.Button(mainframe, text="convert file", command=convertFile, style='C.TButton').grid(column=2, row=5)
ttk.Label(mainframe, textvariable=FILE_CONVERTED_TEXT, foreground="green").grid(column=2, row=6)
ttk.Button(mainframe, text="save new wsm file", command=saveAs, style='C.TButton').grid(column=2, row=7)


for child in mainframe.winfo_children(): 
    child.grid_configure(padx=10, pady=5)


root.mainloop()