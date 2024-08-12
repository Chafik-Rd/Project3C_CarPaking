import PySimpleGUI as sg
# import matplotlib.pyplot as plt
from PIL import Image
import io
import base64
# import app
import GetImage
from threading import Thread

def runapp(frames, img_todrawn=None):
    pass
    # while True:
    #     app.app(frames, img_todrawn)
    
def update():
    # global graph
    # global window
    image = GetImage.getLastImg()
    if image != "SameImage":
        graph.draw_image(data = convert_to_bytes(img=image,resize=(640,480)),location = (0,0))
        print("image updated")
    else:
        pass
    window['-reload-'].update(disabled = False)
    

# Setting Window's theme
sg.theme('DarkAmber')

# Function custom image 
def convert_to_bytes(file_or_bytes=None, resize=None, img=None):
    '''
    Will convert into bytes and optionally resize an image that is a file or a base64 bytes object.
    Turns into  PNG format in the process so that can be displayed by tkinter
    :param file_or_bytes: either a string filename or a bytes base64 image object
    :type file_or_bytes:  (Union[str, bytes])
    :param resize:  optional new size
    :type resize: (Tuple[int, int] or None)
    :return: (bytes) a byte-string object
    :rtype: (bytes)
    '''
    if img:
        pass
    elif isinstance(file_or_bytes, str):
        img = Image.open(file_or_bytes)
    else:
        try:
            img = Image.open(io.BytesIO(base64.b64decode(file_or_bytes)))
        except Exception as e:
            dataBytesIO = io.BytesIO(file_or_bytes)
            img = Image.open(dataBytesIO)

    cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height/cur_height, new_width/cur_width)
        img = img.resize((int(cur_width*scale), int(cur_height*scale)), Image.ANTIALIAS)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    del img
    return bio.getvalue()


run =  [[sg.Combo(['CAM1'],size=(10,1))],
        # [sg.Output(size=(110,30))],
        [sg.Button('RUN',size=(15,2),key='run',disabled = True),
            sg.Checkbox('Image_Pass',font='Any 13',pad=((100,0), (0,0)),key='-image_pass-',enable_events=True),
            sg.Button('View',size=(15,2),key='-view-')]]
    
    
setting = [[sg.Text('Preview image setting',font='Any 15',pad=(300,0))], 
               
        [sg.Graph(
            canvas_size=(640,480),
            graph_bottom_left=(0,480),
            graph_top_right=(640,0),
            key='graph',
            pad=((30,0), (0,0)),
            change_submits=True,
            # enabling drag_submits enables mouse_drags, but disables mouse_up events
            drag_submits=True)
        ],  
          
        [sg.Button(
            button_text='RELOAD',
            size=(15,2),
            pad=((80,0), (0,5)),
            key='-reload-',
            disabled = False),
        sg.Button(
            button_text="UNDO",
            disabled=True,
            size=(15,2),
            key='undo'
        ),
        sg.Button(
            button_text="CLEAR",
            disabled=True,
            size=(15,2),
            key='clear'
        )
        ]
    ]

layout = [[sg.TabGroup([[sg.Tab('Run', run), sg.Tab('Setting', setting)]])]
        #   ,[sg.Exit(size=(15,2),pad=((40,0), (0,5)))]
          ]
               
window = sg.Window('Setting program', layout
                #    ,no_titlebar=True
                   )  
window.Finalize()

graph = window.Element('graph')

graph.draw_image(data = convert_to_bytes(img=GetImage.getLastImg(),resize=(640,480)),location = (0,0))

click = False
rectID = []
tempID = 0
start = []
stop = []

# The Event Loop
while True:   
    event, values = window.read() 

    print(event)
    
    # if close windows      
    if event == sg.WIN_CLOSED or event == 'Exit':
        break  

    if event == '-reload-':  
        t1 = Thread(target=update)
        t1.start()
        window['-reload-'].update(disabled = True) 
                        
    if event == '-run-':
        frames = []
        for i in range(len(start)):
            left = min(start[i][0],stop[i][0])
            right = max(start[i][0],stop[i][0])
            top = min(start[i][1],stop[i][1])
            bottom = max(start[i][1],stop[i][1])
            area = (right-left)*(bottom-top)
            frames.append([i, left, right, top, bottom, area])

        t2 = Thread(target=runapp,args=(frames))
        t2.start()
        
        # if values['-image_pass-']:
        #     result,Available,perf_mon = app.app(3,fTop,fBottom,grid_img)
        # else:
        #     pass
        # result,Available,perf_mon = Detaccar.app(numcar,fTop,fBottom)
        # print("Available slot at : ",Available)
        # print("Process runtime : ",perf_mon)
        # print('')
        # if values['-perf_monitor-']:
        #     update_text = 'Processing time : ' + str(perf_mon)
        #     window['-perf_text-'].update(update_text)

    if click:
        try:
            graph.delete_figure(tempID)
        except:
            pass
        tempID = graph.draw_rectangle(start[-1],values["graph"], line_color='red', line_width = 5)

    if event == 'graph' and not click:
        click = True
        start.append(values["graph"])

    if event == 'graph+UP' and click: 
        click = False
        try:
            graph.delete_figure(tempID)
        except:
            pass
        stop.append(values["graph"])

        rectID.append(graph.draw_rectangle(start[-1], stop[-1], line_color='red', line_width = 5))

        window["undo"].update(disabled=False)
        window["clear"].update(disabled=False)
        window["run"].update(disabled=False)

    if event == 'undo':
        graph.delete_figure(rectID[-1])
        rectID.pop()
        start.pop()
        stop.pop()
        if len(rectID) == 0:
            window["undo"].update(disabled=True)
            window["clear"].update(disabled=True)
            window["run"].update(disabled=True)

    if event == 'clear':
        for ID in rectID:
            graph.delete_figure(ID)

        start = []
        stop = []

        window["undo"].update(disabled=True)
        window["clear"].update(disabled=True)
        window["run"].update(disabled=True)

# Finish up by removing from the screen
window.close()
        
        

