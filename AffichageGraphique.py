from tkinter import *
from tkinter import ttk 
from PIL import Image
from PIL import ImageTk
import main as m
import plateau as p
import IA
import joueur as j
from threading import Timer
import copy
import json
import random
import time

root = Tk()
root.title("Scrabble Deluxe")
root.geometry("810x810")
root.resizable(height=False, width=False)
root.iconbitmap("Logo.ico")
root.configure(bg="#ffc72e")

# Permet d'effacer les elements graphiques contenu dans le parametre frame 
def clearElement(frame):
    for child in frame.winfo_children():
        if type(child) == Frame:
            clearElement(child)
        child.destroy()

class JeuScrabble:
    
    # Initialise les données de jeu
    def __init__(self, fenetre):
        self.infos_joueurs = {}
        self.fenetre = fenetre
        self.nombre_joueur = 2
        self.motsfr = p.generer_dico("COMPACT.txt")
        self.dico_valeur = p.init_dico()
        self.pioche = p.init_pioche(self.dico_valeur)
        self.num_round=1
        self.plateau_jetons = p.init_jetons()
        self.plateau_bonus = p.init_bonus()
        self.tours_passe_consecutif = 0
        self.dico_image = {}
        self.dico_plateau = {}
        self.finit = [0, "premier joueur a finir"]
        self.joueur_actuel=""
        self.mots_deja_place=[]
        

        liste_img = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","interro","McD","McT","LcD","LcT", "Vide"]
        for case in liste_img:
            image = Image.open("MesJetons/{}.png".format(case))
            image = image.resize((50, 50))
            img = ImageTk.PhotoImage(image)
            self.dico_image[case]=img
       

    # Affiche la fenetre d'accueil du jeu            
    def StartFenetre(self):
        
        imageTitre = Image.open("MesJetons/TitreDuJeu.png").resize((720, 180))
        img = ImageTk.PhotoImage(imageTitre)
        LabelTitre = Label(self.fenetre, image=img, bg="#ffc72e")
        LabelTitre.image = img
        LabelTitre.place(x=41,y=41)

        start_buttun = Button(self.fenetre, text="START NEW GAME",width=19 ,font=("courrier", 30), bg="white", fg="#ffc72e", command=self.ChoixParametresJeu)
        start_buttun.place(x=179,y=500)
        start_save_button=Button(self.fenetre, text="START SAVED GAME",width=19, font=("courrier", 30), bg="white", fg="#ffc72e", command=self.ChargerPartie)
        start_save_button.place(x=179,y=600)
    

    # Charge une partie précedemment sauvegardée
    def ChargerPartie(self):
        
        with open("save.json", "r") as read_file:
            data = json.load(read_file)
            
        self.num_round = data[0]
        self.infos_joueurs = data[1]
        self.plateau_jetons = data[2]
        self.pioche = data[3]
        self.plateau_bonus = data[4]
        self.tours_passe_consecutif = data[5]
        self.motsfr = m.generer_dico(data[6])
        self.mots_deja_place = data[7]
        self.duree_partie = time.time()-data[8]
        self.choix_dev = data[9]

        self.fenetre.geometry("1300x810")
        self.AfficheTourJoueur()


    # Affiche la fenetre dans laquelle le joueur choisit les parametres de la partie
    def ChoixParametresJeu(self):
        
        clearElement(self.fenetre)
    
        imageTitreParametres = Image.open("MesJetons/TitreParametres.png").resize((750, 75))
        img = ImageTk.PhotoImage(imageTitreParametres)
        LabelTitreP = Label(self.fenetre, image=img, bg="#ffc72e")
        LabelTitreP.image = img
        LabelTitreP.place(x=32, y=17)
    
        self.JoueurNbFrame = Frame(self.fenetre)
        self.DicoFrame = Frame(self.fenetre)
        self.InfosJoueursFrame = Frame(self.fenetre)

        nb_joueur = [2, 3, 4]
        choix_nombre = IntVar()
        choix_nombre.set(nb_joueur[0])
        for n in range(3):
            bouton = Radiobutton(self.JoueurNbFrame, text = "{} joueurs".format(nb_joueur[n]), font=("courrier", 15), variable = choix_nombre, value = nb_joueur[n], command=lambda : self.ChoixInfosJoueurs(choix_nombre.get()))
            bouton.pack(side =LEFT, padx =62)
        
        self.JoueurNbFrame.place(x=50,y=230)

        diff_dico = ["Compact", "Officiel"]
        choix_dico = StringVar()
        choix_dico.set(diff_dico[0])
        for n in range(2):
            bouton2 = Radiobutton(self.DicoFrame, text = "Dictionnaire {}".format(diff_dico[n]), font=("courrier", 15), variable = choix_dico, value = diff_dico[n], command=lambda : self.ChangementDico(choix_dico.get().upper()))
            bouton2.pack(side =LEFT, padx =72)
    
        self.DicoFrame.place(x=50,y=175)
        self.LabelErreurNom = Label(self.fenetre, text="",font=("courrier", 14, "bold"), bg="#ffc72e" ,fg="red")
        self.LabelErreurNom.place(x=240,y=365)
        self.choix_dev="OFF"
        self.BoutonAdmin = Button(self.fenetre, text="Mode Admin {}".format(self.choix_dev), width=58, font=("courrier", 15, "bold"), bg="purple" ,fg="white", command=self.ModeDev)
        self.BoutonAdmin.place(x=50,y=735)
        self.ChoixInfosJoueurs(self.nombre_joueur)
    

    # Change le dictionnaire qui sera utilisé
    def ChangementDico(self, nom_dico):

        self.motsfr = m.generer_dico(nom_dico+".txt")

    
    # Permet de jouer en mode développeur. Met que des jokers dans la pioche
    def ModeDev(self):

        if self.choix_dev=="OFF":
            self.choix_dev="ON"
            self.BoutonAdmin.configure(text="Mode Admin {}".format(self.choix_dev))
            
        else:
            self.choix_dev="OFF"
            self.BoutonAdmin.configure(text="Mode Admin {}".format(self.choix_dev))
    

    # Permet au joueur de choisir les informations de chaque joueur
    def ChoixInfosJoueurs(self, choix_nombre, num_joueur=0):

        if num_joueur==0:
            self.infos_joueurs={}
            self.nombre_joueur = choix_nombre

        clearElement(self.InfosJoueursFrame)
        

        if num_joueur < (self.nombre_joueur):
            LabelJoueur = Label(self.InfosJoueursFrame, text="Joueur {} :".format(num_joueur+1), font=("courrier", 15))
            LabelJoueur.grid(row=num_joueur, column=0)
            NomJoueur = Entry(self.InfosJoueursFrame, font=("courrier", 15))
            pseudo_defaut=["Albert","Roger","Martin","Louis","Marie","Alice","Céline"]
            NomJoueur.insert (0, random.choice(pseudo_defaut)+"({})".format(num_joueur+1))
            NomJoueur.grid(row=num_joueur, column=1)
            diff_ia=["Pas d'IA","Normale","Extreme"]
            choix_ia=StringVar()
            choix_ia.set(diff_ia[0])
            for n in range(3):
                bouton_ia = Radiobutton(self.InfosJoueursFrame, text = "{}".format(diff_ia[n]), font=("courrier", 15), variable = choix_ia, value = diff_ia[n])
                bouton_ia.grid(row=num_joueur, column=2+n)
            BoutonValide = Button(self.InfosJoueursFrame, text="Valider", font=("courrier", 15), bg="green" ,fg="white", command=lambda: self.verif_data(num_joueur, NomJoueur.get(),choix_ia.get() ))
            BoutonValide.grid(row=num_joueur, column=5)

            
            self.InfosJoueursFrame.place(x=50,y=400)
        else:
            
            self.duree_partie=time.time()
            self.fenetre.geometry("1300x810")
            self.AfficheTourJoueur()
    

    # Complete les informations de chaques joueur en fonction de ce qu'a rentré l'utilisateur
    def verif_data(self, num_joueur, nom_joueur, choix_ia):

        if len(nom_joueur)<=9:

            if choix_ia=="Pas d'IA":
                self.infos_joueurs[str(num_joueur)]={"pseudo": nom_joueur}
                self.infos_joueurs[str(num_joueur)]["main"] = []
                j.completer_main(self.infos_joueurs[str(num_joueur)]["main"], self.pioche)
                self.infos_joueurs[str(num_joueur)]["score"] = 0
                self.infos_joueurs[str(num_joueur)]["IA"] = "NON"
                self.infos_joueurs[str(num_joueur)]["stat"] = [0, "meilleur mot"]
            else:
                self.infos_joueurs[str(num_joueur)]={"pseudo": nom_joueur}
                self.infos_joueurs[str(num_joueur)]["main"] = []
                j.completer_main(self.infos_joueurs[str(num_joueur)]["main"], self.pioche)
                self.infos_joueurs[str(num_joueur)]["score"] = 0
                self.infos_joueurs[str(num_joueur)]["IA"] = "OUI"
                self.infos_joueurs[str(num_joueur)]["stat"] = [0, "meilleur mot"]
                self.infos_joueurs[str(num_joueur)]["diff"] = choix_ia.upper()
            
            self.LabelErreurNom.configure(text="")
            num_joueur+=1
            self.ChoixInfosJoueurs(self.nombre_joueur, num_joueur)
        else:
            self.LabelErreurNom.configure(text="Erreur : Trop de caractères (9 max)")
             
    
    # Affiche le plateau avec des images
    def AffichePlateau(self):
        
        self.FramePlateau = Frame(self.fenetre)

        for ligne in range(15):
                for colonne in range(15):
                    
                    if self.plateau_jetons[ligne][colonne]!= " ":
                        
                        Label1 = Label(self.FramePlateau, image=self.dico_image[self.plateau_jetons[ligne][colonne]])
                        Label1.grid(column=colonne,row=ligne)
                        Label1.bind("<Button-1>", lambda event: self.Recup_Coord(event))
                        self.dico_plateau["{}/{}".format(ligne, colonne)] = Label1

                    elif self.plateau_bonus[ligne][colonne] != "" and self.plateau_jetons[ligne][colonne]== " ":
                        
                        Label1 = Label(self.FramePlateau, image=self.dico_image[self.plateau_bonus[ligne][colonne]])
                        Label1.grid(column=colonne,row=ligne)
                        Label1.bind("<Button-1>", lambda event: self.Recup_Coord(event))
                        self.dico_plateau["{}/{}".format(ligne, colonne)] = Label1

                    else:
                        
                        Label1 = Label(self.FramePlateau, image=self.dico_image["Vide"])    
                        Label1.grid(column=colonne,row=ligne)
                        Label1.bind("<Button-1>", lambda event: self.Recup_Coord(event))
                        self.dico_plateau["{}/{}".format(ligne, colonne)] = Label1
  
        self.FramePlateau.pack(anchor=W)
        

    # Affiche la main du joueur avec des images
    def AfficheMain(self):
        
        self.image_main={}
        i=0
        LabelMain = Label(self.fenetre, bg="#ffc72e", text="Votre Main (Pioche : {}) :".format(len(self.pioche)), font=("courrier", 17, "bold") )
        LabelMain.place(x=910, y=62)
        for lettre in self.joueur_actuel["main"]:
            if  lettre =="?":
                image = Image.open("MesJetons/interro.png")
            else:
                image = Image.open("MesJetons/{}.png".format(lettre))
            image = image.resize((63, 63))
            img = ImageTk.PhotoImage(image)
            self.image_main["{}".format(i)] = img
            Label1 = Label(self.FrameJoueurMain, image=img, bg="#ffc72e")         
            Label1.grid(column=i,row=0)
            i+=1
        self.FrameJoueurMain.place(x=820, y=100)
    

    # Change la valeur de la direction
    def Changer_Direction(self):

        if self.direction == "droite":
            self.direction = "bas"
        else:
            self.direction = "droite"
        self.LabelDirection.configure(text="Direction actuel : {}".format(self.direction.upper()))
    

    # Recupère les coordonnées du click du joueur sur plateau et le fait correspondre à [ligne/colonne]
    def Recup_Coord(self, event):

        coords_widget = event.widget.grid_info()
        self.coordonnees = [coords_widget["row"], coords_widget["column"]]
        self.LabelPosition.configure(text="Position actuelle : Colonne = {} et Ligne = {}".format(self.coordonnees[1]+1, self.coordonnees[0]+1))


    # Change la main du joueur et passe au tour d'apres
    # Renvoie un message d'erreur si le joueur n'a pas les lettres nécessaires
    def Changer_Main_Passe(self, ll, lm):
        check = j.echanger(ll,lm, self.pioche)
        if not check:
            self.tours_passe_consecutif+=1
            self.AfficheMain()
            self.LabelAide.configure(text="{} passe son tour".format(self.joueur_actuel["pseudo"]), fg="black")

            self.fenetre.after_idle(lambda : self.AjouterDelaiFinTour(1.5))
        else:
            self.LabelAide.configure(text="Vous n'avez pas les lettres necessaires", fg="red")


    # Passe au tour suivant et si la main du joueur et le sac sont vide, enclenche la procédure de fin de partie
    def TourSuivant(self):
        
        if len(self.joueur_actuel["main"]) == 0 and len(self.pioche) == 0:
            self.finit = [1, self.joueur_actuel]
            
        self.num_round+=1
        self.AfficheTourJoueur()


    # Affiche le classement en direct
    def AfficheScore(self):
        dicoScore = {}
        classement = []
        for x,y in sorted(self.infos_joueurs.items(), key=lambda x: x[1]["score"], reverse=True):
            classement.append(y)
        for pos in range(len(classement)):
            self.LabelScore = Label(self.fenetre, text="{} | {} : {} points".format(pos+1,classement[pos]["pseudo"], classement[pos]["score"]),font=("courrier", 14, "bold"), bg="#ffc72e" )
            dicoScore[pos]=self.LabelScore
            self.LabelScore.place(x=817+(235 if pos>1 else 0), y=630+((pos%2)*37))


    # Options développeur que l'utilisateur peut appeler
    def ChoixOptionDev(self, event):
        
        choix = self.comboOptions.get()

        if choix=="Remplir la main de jocker":
            self.joueur_actuel["main"]=["?","?","?","?","?","?","?"]
            self.AfficheMain()
            self.BoutonAideAlea.config(state=DISABLED)
            self.BoutonAideMeilleur.config(state=DISABLED)
        elif choix=="Rétablir la main d'origine" and self.joueur_actuel["main"]==["?","?","?","?","?","?","?"]:
            self.joueur_actuel["main"]=self.copie_main
            self.BoutonAideAlea.config(state=NORMAL)
            self.BoutonAideMeilleur.config(state=NORMAL)
            self.AfficheMain()
        elif choix=="Forcer la victoire":
            self.finit=[1, self.joueur_actuel]
        elif choix=="Forcer la victoire (tours passés)":
            self.tours_passe_consecutif=self.nombre_joueur*3
            

    # Affiche toute les infos necessaires au joueur pour qu'il puisse jouer son tour
    def AfficheTourJoueur(self):

        clearElement(self.fenetre)
        
        self.FrameJoueurMain = Frame(self.fenetre)
        
        # Definit le joueur actuel
        self.joueur_actuel = self.infos_joueurs[str((self.num_round - 1) % len(self.infos_joueurs))]
        
        if self.finit[0] == 0 and self.tours_passe_consecutif < self.nombre_joueur*3:

            self.AffichePlateau()
            self.AfficheMain()
            
            self.direction = "droite"
            self.coordonnees = [7,7]

            LabelNom = Label(self.fenetre, text="Tour de {} (round n°{})".format(self.joueur_actuel["pseudo"], self.num_round),font=("courrier", 20, "bold underline"), bg="#ffc72e" )
            LabelNom.place(x=821,y=10)

            BoutonSauvegarder = Button(self.fenetre, text="Sauvegarder La Partie", width=38, font=("courrier", 15, "bold"), bg="blue" ,fg="white", command=lambda : m.sauvegarder(self.num_round, 
            self.infos_joueurs, self.plateau_jetons, self.pioche, self.plateau_bonus, self.tours_passe_consecutif, self.motsfr, self.mots_deja_place, time.time()-self.duree_partie, self.choix_dev))
        
            BoutonSauvegarder.place(x=821,y=760)

            self.AfficheScore()
            
            self.LabelAide = Label(self.fenetre, text="",font=("courrier", 15, "bold"), bg="#ffc72e",fg="white" )
            self.LabelAide.place(x=818,y=305)

            if self.choix_dev=="ON":
                    self.LabelDev = Label(self.fenetre, text="Options Développeurs : ",font=("courrier", 15, "bold"), bg="#ffc72e")
                    self.LabelDev.place(x=820,y=370)
                    self.comboOptions = ttk.Combobox(self.fenetre, font=("courrier", 14), values=["Remplir la main de jocker","Rétablir la main d'origine", "Forcer la victoire","Forcer la victoire (tours passés)"],state="readonly")
                    self.comboOptions.current(0)
                    self.comboOptions.place(x=1050,y=370)
                    self.comboOptions.bind("<<ComboboxSelected>>", self.ChoixOptionDev)
                    if self.joueur_actuel["IA"]=="OUI":
                        self.comboOptions.configure(values=["Forcer la victoire","Forcer la victoire (tours passés)"])
                        self.comboOptions.current(0)

            if self.joueur_actuel["IA"]=="OUI":
            
                self.fenetre.after_idle(lambda : self.AjouterDelaiIa(0.5))
                
            else:
    

                # Affiche les widgets nécessaires au bon déroulement du tour du joueur
                BoutonChangerMain = Button(self.fenetre, text="Passer Son Tour/Changer Sa Main", width=38,font=("courrier", 15, "bold"), bg="#bc8dff" ,fg="white", command=lambda :self.Changer_Main_Passe(LettreAChanger.get().upper(), self.joueur_actuel["main"]))
                BoutonChangerMain.place(x=821,y=175)
                LettreAChanger = Entry(self.fenetre, width=42, font=("courrier", 15))
                LettreAChanger.place(x=821,y=222)
                
                self.copie_main=list(self.joueur_actuel["main"])

                self.BoutonAideAlea = Button(self.fenetre, text="Mot Aléatoire", state=NORMAL,width=18, font=("courrier", 15, "bold"), bg="#bc8dff" ,fg="white", command=self.AideMotAlea)
                self.BoutonAideAlea.place(x=821,y=257)
                self.BoutonAideMeilleur = Button(self.fenetre, text="Meilleur Mot", state=NORMAL,width=18, font=("courrier", 15, "bold"), bg="#bc8dff" ,fg="white",command=self.AideMeilleurMot)
                self.BoutonAideMeilleur.place(x=1062,y=257)
                

                BoutonDirection = Button(self.fenetre, text="Changer la Direction", width=38, font=("courrier", 15, "bold"), bg="#70b9ff" ,fg="white", command=self.Changer_Direction)
                BoutonDirection.place(x=821,y=578)
                self.MotUtilisteur = Entry(self.fenetre, width=42, font=("courrier", 15))
                self.MotUtilisteur.place(x=821,y=465)
                LabelNom = Label(self.fenetre, text="Quel mot voulez vous jouer ?",font=("courrier", 17, "bold"), bg="#ffc72e" )
                LabelNom.place(x=885,y=430)
                self.LabelDirection = Label(self.fenetre, text="Direction actuel : {}".format(self.direction.upper()),font=("courrier", 15, "bold"), bg="#ffc72e")
                self.LabelDirection.place(x=821,y=538)
                self.LabelPosition = Label(self.fenetre, text="Position actuelle : Colonne = {} et Ligne = {}".format(self.coordonnees[1]+1, self.coordonnees[0]+1),font=("courrier", 15, "bold"), bg="#ffc72e" )
                self.LabelPosition.place(x=821,y=500)

                BoutonValider = Button(self.fenetre, text="Valider", width=38, font=("courrier", 15, "bold"), bg="#87d742" ,fg="white", command=lambda : self.Verif_Place_Mot(self.MotUtilisteur.get().upper(), self.direction, self.coordonnees))
                BoutonValider.place(x=821,y=710)

                self.LabelErreur = Label(self.fenetre,font=("courrier", 13, "bold"), bg="#ffc72e" ,fg="red")
                self.LabelErreur.place(x=820,y=400)
        else:
            self.FinDePartie()
    

    # Enclenche le processus de fin de partie
    def FinDePartie(self):
        
        clearElement(self.fenetre)
        self.fenetre.geometry("1620x810")
        self.AffichePlateau()
        self.duree_partie=round((time.time()-self.duree_partie))
        
        imageVictoire = Image.open("MesJetons/Victoire.png").resize((700, 90))
        img = ImageTk.PhotoImage(imageVictoire)
        LabelTitreV = Label(self.fenetre, image=img, bg="#ffc72e")
        LabelTitreV.image = img
        LabelTitreV.place(x=860, y=10)

        
        self.premier_a_finir = self.finit[1]
        
        self.Stats()
    

    # Ajoute un delai avant que l'IA place son mot pour evité qu'elle le place trop vite et fasse buger le jeu
    def AjouterDelaiIa(self, time):
        t = Timer(time, lambda : self.PlaceMotIa())  
        t.start()

    # Ajoute un délai avant de lancer le tour suivant
    def AjouterDelaiFinTour(self, time):
        t = Timer(time, lambda : self.TourSuivant())
        t.start()


    # Affiche à l'utilisateur un mot aléatoire qu'il peut faire
    def AideMotAlea(self):
        
        mot_aide = IA.proposition_mot_posable(self.joueur_actuel["main"], self.plateau_jetons, self.motsfr, self.mots_deja_place)
        
        if mot_aide != False:
            coords_inverse = mot_aide[1][1] + 1, mot_aide[1][0] + 1
            self.LabelAide.configure(text="Aide : {} en {} vers le/la {}".format(mot_aide[0],coords_inverse,mot_aide[2]), fg="black")
            self.MotUtilisteur.delete(0, len(self.MotUtilisteur.get()))
            self.MotUtilisteur.insert(0, mot_aide[0])
            self.coordonnees=mot_aide[1]
            self.direction=mot_aide[2]
            self.LabelDirection.configure(text="Direction actuel : {}".format(self.direction.upper()))
            self.LabelPosition.configure(text="Position actuelle : Colonne = {} et Ligne = {}".format(self.coordonnees[1]+1, self.coordonnees[0]+1))
        else:
            self.LabelAide.configure(text="Aide : Vous ne pouvez rien faire", fg="red")
    
    
    # Affiche à l'utilisateur le meilleur mot qu'il peut faire
    def AideMeilleurMot(self):
        mot_aide = IA.meilleur_mot_posable(self.joueur_actuel["main"], self.plateau_jetons, self.plateau_bonus, self.motsfr, self.mots_deja_place)
        if mot_aide != False:
            coords_inverse = mot_aide[1][1] + 1, mot_aide[1][0] + 1
            self.LabelAide.configure(text="Aide : {} en {} vers le/la {} ({} pts) ".format(mot_aide[0], coords_inverse, mot_aide[2], mot_aide[4]), fg="black")
            self.MotUtilisteur.delete(0, len(self.MotUtilisteur.get()))
            self.MotUtilisteur.insert(0, mot_aide[0])
            self.coordonnees=mot_aide[1]
            self.direction=mot_aide[2]
            self.LabelDirection.configure(text="Direction actuel : {}".format(self.direction.upper()))
            self.LabelPosition.configure(text="Position actuelle : Colonne = {} et Ligne = {}".format(self.coordonnees[1]+1, self.coordonnees[0]+1))
        else:
            self.LabelAide.configure(text="Aide : Vous ne pouvez rien faire", fg="red")


    # Verifie le mot de l'utilisateur et s'il est bon, le place sur le plateau
    def Verif_Place_Mot(self, mot_uti, direction, coords):
        
        
        if mot_uti!="" and mot_uti in self.motsfr:
            
            nouvels_infos = p.mot_cree(mot_uti, self.plateau_jetons, direction,coords)
            
            mot_uti = nouvels_infos[0]
            coords = nouvels_infos[1]

            check = p.tester_placement_mot(self.plateau_jetons, coords, direction, mot_uti, self.joueur_actuel["main"], self.motsfr)
            if check[0]:
                nouvelle_infos = p.mot_cree(mot_uti, self.plateau_jetons, direction, coords)
                choix_uti = [nouvelle_infos[0], nouvelle_infos[1], direction, check[1]]
                
                plateau_avant = copy.deepcopy(self.plateau_jetons)
                p.placer_mot(self.plateau_jetons, choix_uti[0], choix_uti[1], choix_uti[2], choix_uti[3], self.joueur_actuel["main"], self.pioche,
                           1)
                self.mots_deja_place.append([choix_uti[0], choix_uti[1], choix_uti[2]])
                valeur_du_coup = p.calculer_score(self.plateau_jetons, plateau_avant, choix_uti[0], choix_uti[1],
                                                choix_uti[2],
                                                self.plateau_bonus, choix_uti[3])
                self.joueur_actuel["score"] += valeur_du_coup

                if valeur_du_coup >= self.joueur_actuel["stat"][0]:
                    self.joueur_actuel["stat"] = [valeur_du_coup, choix_uti[0]]
                
                coordonnees_inverse = [choix_uti[1][1]+1,choix_uti[1][0]+1]
                self.LabelAide.configure(text="{} ==> {} en {} vers le/la {} \n {} gagne {} points"
                .format(self.joueur_actuel["pseudo"],choix_uti[0], coordonnees_inverse, choix_uti[2],self.joueur_actuel["pseudo"], valeur_du_coup), fg="black")
                
                self.AfficheScore()
                self.tours_passe_consecutif = 0
                
                self.fenetre.after_idle(lambda : self.AjouterDelaiFinTour(1.5))
            else:
                self.LabelErreur.configure(text="Erreur : {}".format(check[1]))
                
        else:
            self.LabelErreur.configure(text="Erreur : Ce mot n'existe pas")
            


    # Place un mot automatiquement quand c'est le tour d'une IA
    def PlaceMotIa(self):
        
        if self.joueur_actuel["diff"]=="NORMALE":
            mot_aide = IA.proposition_mot_posable(self.joueur_actuel["main"], self.plateau_jetons, self.motsfr,self.mots_deja_place)
        else:
            mot_aide = IA.meilleur_mot_posable(self.joueur_actuel["main"], self.plateau_jetons, self.plateau_bonus, self.motsfr,self.mots_deja_place)
        if not mot_aide:
            j.echanger(self.joueur_actuel["main"],self.joueur_actuel["main"], self.pioche)
            self.tours_passe_consecutif += 1
            self.AfficheMain()
            self.LabelAide.configure(text="{} passe son tour".format(self.joueur_actuel["pseudo"]), fg="black")

            self.fenetre.after_idle(lambda : self.AjouterDelaiFinTour(1.5))
        else:
            coordonnees_inverse = [mot_aide[1][1] + 1, mot_aide[1][0] + 1]
                
                    
            plateau_avant = copy.deepcopy(self.plateau_jetons)
            p.placer_mot(self.plateau_jetons, mot_aide[0], mot_aide[1], mot_aide[2], mot_aide[3], self.joueur_actuel["main"], self.pioche, 1)

            self.mots_deja_place.append([mot_aide[0], mot_aide[1], mot_aide[2]])

            valeur_du_coup = p.calculer_score(self.plateau_jetons, plateau_avant, mot_aide[0], mot_aide[1],mot_aide[2],self.plateau_bonus, mot_aide[3])

            self.joueur_actuel["score"] += valeur_du_coup
            if valeur_du_coup >= self.joueur_actuel["stat"][0]:
                self.joueur_actuel["stat"] = [valeur_du_coup, mot_aide[0]]

            self.LabelAide.configure(text="{} ==> {} en {} vers le/la {} \n {} gagne {} points"
            .format(self.joueur_actuel["pseudo"],mot_aide[0], coordonnees_inverse, mot_aide[2],self.joueur_actuel["pseudo"], valeur_du_coup), fg="black")
            
            self.AfficheScore()

            self.tours_passe_consecutif=0
            
            self.fenetre.after_idle(lambda : self.AjouterDelaiFinTour(1.5)) 


    # Relance une autre partie
    def rejouer(self):
        clearElement(self.fenetre)
        self.fenetre.geometry("810x810")
        self.__init__(self.fenetre)
        self.StartFenetre()


    # Affiche les statistiques de la partie et des joueurs et le classement à la fin de la partie
    def Stats(self):
        classement=[]

        if self.tours_passe_consecutif>=self.nombre_joueur*3:
            print(1)
            for indice in self.infos_joueurs:
                self.infos_joueurs[indice]["score"] -= p.valeur_mot(self.infos_joueurs[indice]["main"])
                
        else:
            print(2)
            for indice in self.infos_joueurs:
                self.premier_a_finir["score"] += p.valeur_mot(self.infos_joueurs[indice]["main"])
                self.infos_joueurs[indice]["score"] -= p.valeur_mot(self.infos_joueurs[indice]["main"])
                self.premier_a_finir["score"] += p.valeur_mot(self.premier_a_finir["main"])
               
        for x,y in sorted(self.infos_joueurs.items(), key=lambda x: x[1]["score"], reverse=True):
            classement.append(y)

        LabelNomClassement = Label(self.fenetre, text="Classement :",font=("courrier", 18, "bold underline"), bg="#ffc72e")
        LabelNomClassement.place(x=860, y=260)
        LabelNbRound = Label(self.fenetre, text="Nombre de tours joués : {} (en {}min {}sec)".format(self.num_round-1, self.duree_partie//60, self.duree_partie%60),font=("courrier", 18, "bold"), bg="#ffc72e")
        LabelNbRound.place(x=1100,y=260)
        
        BoutonRejouer = Button(self.fenetre, text="Rejouer", width=30, font=("courrier", 15, "bold"), bg="green" ,fg="white", command=self.rejouer)
        BoutonRejouer.place(x=830,y=750)
        BoutonQuitter = Button(self.fenetre, text="Quitter", width=30, font=("courrier", 15, "bold"), bg="red" ,fg="white", command=lambda : self.fenetre.destroy())
        BoutonQuitter.place(x=1220,y=750)

        
        LabelGagnant = Label(self.fenetre, text="de \n{}".format(classement[0]["pseudo"]),font=("courrier", 40, "bold"), bg="#ffc72e")
        LabelGagnant.place(x=1130,y=105)
            
        dico_label_classement={}
           
        for podium in range(len(classement)):
            LabelPodium = Label(self.fenetre, text="Bien joué a {} qui remporte la {}er/éme place avec {} points !!!".format(classement[podium]["pseudo"],podium + 1,classement[podium]["score"]) ,font=("courrier", 15, "bold"), bg="#ffc72e")         
            LabelStat = Label(self.fenetre, text="Son meilleur coup est le mot {} qui lui a rapporté {} points !".format(classement[podium]["stat"][1],
                                                                                          classement[podium]["stat"][0]) ,font=("courrier", 15, "bold"), bg="#ffc72e")
            dico_label_classement[str(podium)]=[LabelPodium,LabelStat]
            LabelPodium.place(x=860,y=310+podium*100)                                                                                   
            LabelStat.place(x=860,y=340+podium*100)                                                                                 



if __name__ == "__main__":
    Plateau = JeuScrabble(root)
    Plateau.StartFenetre()
    root.mainloop()