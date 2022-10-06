from bs4 import BeautifulSoup
from tkinter import filedialog
from tkinter import *
import customtkinter
import json

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Global variables
        self.WW6_FILE_PATH = None
        self.WSM_FILE_PATH = None
        self.WW6_FILE_NAME = StringVar()
        self.WSM_FILE_NAME = StringVar()
        self.FILE_CONVERTED_TEXT = StringVar()
        self.FILE_CONVERTED_TEXT_COLOR = None
        self.Bs_wsm_data = None
        self.width = 600
        self.height = 280
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.window_position_x = int((self.screen_width/2) - (self.width/2))
        self.window_position_y = int((self.screen_height/2) - (self.height/2))
        self.logo = PhotoImage(file='ww6-wsm_logo.png')
        self.receiver_list = None

        with open('receiver_list.json','r') as file:
            x = file.read()
            self.receiver_list = json.loads(x)


        # CustomTK setup
        self.title("WW6 to WSM converter")
        # self.minsize(0, 1000)
        self.geometry(f"{self.width}x{self.height}+{self.window_position_x}+{self.window_position_y}")

        # Column configuration
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=1)

        self.logoLabel = customtkinter.CTkLabel(master=self, image=self.logo)
        self.logoLabel.grid(column=2, row=1, rowspan=3, sticky="NS")

        # File select section
        self.button1 = customtkinter.CTkButton(master=self, text='open WW6 file', command=self.open_ww6)
        self.button1.grid(column=1, row=1, padx=10, pady=10,)

        self.button2 = customtkinter.CTkButton(master=self, text='open WSM file', command=self.open_wsm)
        self.button2.grid(column=3, row=1, padx=10, pady=10, )

        self.label1 = customtkinter.CTkLabel(master=self, text='Wireless workbench file:')
        self.label1.grid(column=1, row=2,padx=10, pady=10)

        self.label2 = customtkinter.CTkLabel(master=self,fg_color="gray75", corner_radius=5, text_color='black', textvariable=self.WW6_FILE_NAME)
        self.label2.grid(column=1, row=3,padx=10, pady=10)

        self.label3 = customtkinter.CTkLabel(master=self, text='WSM file:')
        self.label3.grid(column=3, row=2,padx=10, pady=10)

        self.label4 = customtkinter.CTkLabel(master=self,fg_color="gray75", corner_radius=5, text_color='black', textvariable=self.WSM_FILE_NAME)
        self.label4.grid(column=3, row=3,padx=10, pady=10)

        # Generate and save section

        self.button3 = customtkinter.CTkButton(master=self, text='Convert file', command=self.convertFile)
        self.button3.grid(column=2, row=4, pady=10, sticky='EW')

        self.label5 = customtkinter.CTkLabel(master=self, textvariable=self.FILE_CONVERTED_TEXT)
        self.label5.grid(column=1, row=5, columnspan=3, pady=5, sticky='NS')

        self.button4 = customtkinter.CTkButton(master=self, text='Save new WSM file', command=self.saveAs)
        self.button4.grid(column=2, row=6, )

    def changeColor(self,label,color):

        label.configure(text_color=color)

    def saveAs(self):
        self.Bs_wsm_data

        f = filedialog.asksaveasfile(mode='w', defaultextension=".wsm")
        if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        text2save = self.Bs_wsm_data.prettify()
        f.write(text2save)
        f.close()

    def open_ww6(self):

        self.WW6_FILE_PATH = (filedialog.askopenfilename(filetypes=(('wireless workbench 6', "*.shw"),)))
        self.WW6_FILE_NAME.set(self.WW6_FILE_PATH.split('/')[-1])

        self.FILE_CONVERTED_TEXT.set('')


    def open_wsm(self):

        self.WSM_FILE_PATH = filedialog.askopenfilename(filetypes=(('WSM file', "*.wsm"),))
        self.WSM_FILE_NAME.set(self.WSM_FILE_PATH.split('/')[-1])

        self.FILE_CONVERTED_TEXT.set('')

    def matchReceiverToFreqBand(self, receiver):
        if any(x['model'] == receiver['model'] for x in self.receiver_list):
            for y in self.receiver_list:
                if y['model'] == receiver['model']:
                    knownBands = y['bands']
                    for band in knownBands:
                        receiverRange = knownBands[band]
                        if receiver['start'] == receiverRange['start'] and receiver['end'] == receiverRange['end']:
                            receiver['band'] = band.lower()
                            break
        elif any(y['model'] != receiver['model'] for y  in self.receiver_list):
            print("could'nt find that specific receiver model")
        
        return receiver

    def setNewFrequentie(self,receiver, freqPlot):
        newFreq = None

        for freq in freqPlot:
            
            if freq['model'] == receiver['model'] and freq['band'] == receiver['band'] and freq['freeToUse'] == True: 
                newFreq = freq['value']
                freq['freeToUse'] = False
                break
            else:
                continue

        return newFreq

    def convertFile(self):
      
        if self.WW6_FILE_PATH != None and len(self.WW6_FILE_PATH) > 0 and self.WSM_FILE_PATH != None and len(self.WSM_FILE_PATH) > 0:
            try:
                #   Variables for creating specific structures so assigning data becomes easyer
                ww6_freq_plot = []

                #   Open and assign to variable both the ww6 and wsm file
                with open(self.WW6_FILE_PATH, 'r') as ww6_file:
                    ww6_data = ww6_file.read()

                with open(self.WSM_FILE_PATH, 'r') as wsm_file:
                    wsm_data = wsm_file.read()

                #   Create Bs4 objects from the read data
                Bs_ww6_data = BeautifulSoup(ww6_data, 'xml')
                self.Bs_wsm_data = BeautifulSoup(wsm_data, 'xml')

                #   Assign all instances of a freq entry found in the ww6 file to an array
                freq_entry = Bs_ww6_data.find_all('freq_entry')

                #   Assing all instances of a receiver found in the wsm file to an array
                receicers = self.Bs_wsm_data.find_all('Receiver')

                #   For each freq entry found in the ww6 file extract the frequency value and the name of the freq band
                #   and then add those as an sub array to the ww6_freq_plot array
                for item in freq_entry:
                    value = item.find('value').contents[0]
                    band = item.find('band').contents[0].lower()

                    if len(item.find('model').contents) > 0:
                        model = item.find('model').contents[0].replace(' ','')
                    else:
                        model = 'Spare Frequentie'

                    new_freq = {
                        "model":model, 
                        "band":band, 
                        "value":value, 
                        "freeToUse":True
                        }
                    
                    ww6_freq_plot.append(new_freq)


                #   for each instance of an receiver object found in the wsm file extract: lower freq limit, upper freq limit,
                #   current frequency and uniqe id. assign a band name according to the upper and lower freq limit
                #   loop through each freq in the ww6_freq_plot array and if the band name corresponds with the assignd
                #   band name and the is free value equals True assign the frequency as new_freq, then break out of the loop and continue with the next receiver.
                #   do this for each receiver and when done write to a new .wsm file.  

                for item in receicers:
                    
                    lower_freq_limit = item.find('LowerFrequencyLimit').contents[0]
                    uper_freq_limit = item.find('UpperFrequencyLimit').contents[0]
                    current_frequency = item.find('CurrentFrequency')
                    receiver_type = item.get('Type')


                    receiver = {
                        "model":receiver_type,
                        "band": None,
                        "currentFreq":current_frequency.contents[0],
                        "start":lower_freq_limit,
                        "end":uper_freq_limit
                    }

                    receiver = self.matchReceiverToFreqBand(receiver)

                    new_freq = self.setNewFrequentie(receiver,ww6_freq_plot)

                    print(current_frequency)
                    print(new_freq)

                    current_frequency.string = new_freq

                    print(current_frequency)


        



                self.changeColor(self.label5,'#4cb944')
                self.FILE_CONVERTED_TEXT.set('Sucsessfully converted file!')
            except Exception as e:
                print(e)
                self.changeColor(self.label5,'#DA2C38')
                self.FILE_CONVERTED_TEXT.set('Houston we have a problem!')

        else:
            self.changeColor(self.label5,'#DA2C38')
            self.FILE_CONVERTED_TEXT.set('Hmm it seems like we are missing a file or two!')

if __name__ == "__main__":
    app = App()
    app.mainloop()