import threading
import time
import tkinter
import pandas as pd
import cv2 as cv
import serial

# Initialisation de la communication avec la carte arduino
arduino = serial.Serial(port = 'COM3', baudrate = 115200, timeout =.1)

"""
Send_Data(data) permet d'envoyer de la data vers la carte arduino
---PARAMETRE---
data : data à envoyer vers la arduino
"""
def Send_Data(data):
    arduino.write(bytes(data, 'utf-8'))


"""
read() permet de lire la data que la arduino envoie.
Elle retourne la data lu en string.
"""
def read():
     return arduino.readline().decode() #lit en format string


"""
Echelonnage(matLength, posMoy) permet d'échelonner la position moyenne de l'objet 
par rapport à la taille de l'image.
Elle renvoie un tableau posEchelonnee qui contient les coordonnées en pourcentage selon x et y.
---PARAMETRES---
matLength : format de l'image
posMoy : coordonnées brutes moyenne de l'objet
"""
def Echelonnage(matLength, posMoy):
    posEchelonnee = [0, 0]
    
    distAxisI = (matLength[0] / 2) - posMoy[0]
    distAxisJ = posMoy[1] - (matLength[1] / 2)
    
    posEchelonnee[0] = int((distAxisI * 100) / (matLength[1] / 2))
    posEchelonnee[1] = int((distAxisJ * 100) / (matLength[1] / 2))
    
    return posEchelonnee


"""
fonction capture() permet la capture d'image par la caméra et
calcule la position moyenne dans l'image de l'objet de couleur rouge (défini ainsi pour notre projet)
Afin de parcourir rapidement chaque image, un pixel sur deux dans le sens de la longueur et de la largeur 
sont traité
"""
def capture(init_x, init_y):
    ret, frame = cam.read()
    if not ret:
        print("ERROR")
        Send_Data("ERROR")
        return([-1, -1])
    else:
        resize = cv.resize(frame,(1280, 720), interpolation = cv.INTER_LINEAR)
        cv.imwrite("imagerouge.png", resize)
        #cv.imshow("test", resize)
        posmoyenne = [0, 0]       
        k = cv.waitKey(1)
        print("screenshot taken")
        mat = frame
        matLength = mat.shape
        redcount = 0
        img = tkinter.PhotoImage(file = "imagerouge.png")
        graph.delete("all")
        graph.create_image(640, 360, image = img)
        graph.update()
        for i in range (0, matLength[0], 2):
            for j in range (0, matLength[1], 2):
                if frame[i, j, 2] > 180 and frame[i, j, 1] < 100 and frame[i, j, 0] < 100:
                    posmoyenne[0] += i
                    posmoyenne[1] += j
                    redcount += 1
        if redcount == 0:
            #Retour à la position initiale
            #data = str(-0.9*init_x) + ";" + str(-0.9*init_y)
            #print(data)
            Send_Data("ERROR")
            time.sleep(0.5)
            return([-1, -1])
        else: 
            posmoyenne[0] = posmoyenne[0] / redcount
            posmoyenne[1] = posmoyenne[1] / redcount
            posmoyenne[0] = posmoyenne[0] * 720 / matLength[0]
            posmoyenne[1] = posmoyenne[1] * 1280 / matLength[1]
            return posmoyenne


"""
fonction suivi() permet le suivi de l'objet rouge par un pointeur sur l'interface
"""
def suivi():
    init_x = 0
    init_y = 0
    commencer["state"] = tkinter.DISABLED
    quitter["state"] = tkinter.DISABLED
    effacer["state"] = tkinter.DISABLED
    stop["state"] = tkinter.NORMAL
    t = threading.Thread(target = finsuivi)  
    t.start()
    count = 0
    while t.is_alive():
        position = capture(init_x, init_y)
        newx = position[1]
        newy = position[0]
        if (newx < 0 or newy < 0) and count > 0:
            stop["state"]=tkinter.DISABLED
            effacer["state"] = tkinter.DISABLED
            export["state"] = tkinter.DISABLED
            quitter["state"] = tkinter.DISABLED
            warning = tkinter.Tk()
            warning.title('Warning')
            eval_ = warning.nametowidget('.').eval
            eval_('tk::PlaceWindow %s center' % warning)
            tkinter.Label(warning, text = "La caméra ne détecte plus l'objet à suivre.", font = ("Arial")).pack(padx = 10, pady = 10)
            tkinter.Button(warning, text = 'Ok', font = ("Arial"), command = warning.destroy).pack(padx = 10, pady = 10)
            break
        elif newx > 0 and newy > 0:
            posEchelonnee = Echelonnage([720,1280], position)
            
            #Calcul pour retour à la position initiale
            init_x += posEchelonnee[1]
            init_y += posEchelonnee[0]
            
            data = str(posEchelonnee[1]) + ";" + str(posEchelonnee[0])
            Send_Data(data)
            while(read() != "ok"):
                time.sleep(0.05)
            print("data ", data)
            count += 1
            posx.append(newx)
            posy.append(newy)
            if len(posx) >= 1:               
                graph.create_oval(newx - 40, newy - 40, newx + 40, newy + 40, width = 5, outline = "red")
                graph.update()


"""
fonction finsuivi() permet d'arrêter le processus de suivi
"""
def finsuivi():
    quitter["state"] = tkinter.DISABLED
    commencer["state"] = tkinter.DISABLED
    stop["state"] = tkinter.NORMAL
    effacer["state"] = tkinter.DISABLED
    export["state"] = tkinter.DISABLED
    while 0 < 1:
        if(stop["state"] == tkinter.DISABLED):
            break
    effacer["state"] = tkinter.NORMAL
    export["state"] = tkinter.NORMAL
    quitter["state"] = tkinter.NORMAL


"""
fonction stopper() permet de quitter le programme
"""
def stopper():
    stop["state"] = tkinter.DISABLED


"""
fonction effacer_graph() permet d'effacer les données du graphe actuel
afin de recommencer un suivi
"""
def effacer_graph():
    posx.clear()
    posy.clear()
    graph.delete('all')
    graph.update()
    effacer["state"] = tkinter.DISABLED
    export["state"] = tkinter.DISABLED
    commencer["state"] = tkinter.NORMAL


"""
fonction excel() permet d'exporter le graphe dans un fichier csv avec 
l'historique des coordonnées de l'objet
"""
def excel():
    export["state"] = tkinter.DISABLED
    fichier = pd.DataFrame({"x": posx, "y": posy})
    print(fichier)
    fichier.to_csv('donnees.csv')



if __name__ == "__main__":
    posx = []
    posy = []

    cam = cv.VideoCapture(0) #L'état 0 signifie allumage de la cam
    cv.namedWindow("Webcam App")

    root = tkinter.Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight() #récupère la taille de l'écran
    #root.geometry("%dx%d" % (w, h)) #fixe la taille de la fenêtre à la taille de l'écran
    root.configure(bg = "black")

    #permet de proportionner les différents éléments à la taille de la fenêtre grâce au système de grid
    tkinter.Grid.rowconfigure(root, 0, weight=1) 
    tkinter.Grid.columnconfigure(root, 0, weight=1) 
    tkinter.Grid.rowconfigure(root, 1, weight=1)

    graph = tkinter.Canvas(root, highlightthickness = 0)
    graph.grid(row=0, column=0, rowspan=2, columnspan=2, sticky = "NSEW")


    commencer = tkinter.Button(root, command=suivi, text="Start", fg = "black", bg= "grey", font=("Arial", 50))
    commencer.grid(row = 2, column = 0, sticky = "NSEW")

    quitter = tkinter.Button(root, command = root.destroy, text = "Quitter", bg = "grey", fg = "black", font = ("Arial", 50) )
    quitter.grid(row = 2, column = 2, sticky = "NSEW")


    stop = tkinter.Button(root, command = stopper, text = "Stop", bg = "grey", fg = "black", font = ("Arial", 50) )
    stop.grid(row=2, column=1, sticky="NSEW")


    effacer = tkinter.Button(root, command = effacer_graph, text = "Effacer", bg = "grey", fg = "black", font = ("Arial", 50) )
    effacer.grid(row=0, column=2, sticky="NSEW")


    export = tkinter.Button(root, command = excel, text = "Export excel", bg = "grey", fg = "black", font = ("Arial", 50) )
    export.grid(row = 1, column = 2, sticky = "NSEW")

    root.mainloop()