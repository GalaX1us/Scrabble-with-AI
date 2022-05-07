from random import *
import copy
from json import *
import time
import joueur as jo
import IA

# Initialise le nombre d'occurence et la valeur de chaque lettre
def init_dico():
    return {
        "A": {"val": 1, "occ": 9},
        "B": {"val": 3, "occ": 2},
        "C": {"val": 3, "occ": 2},
        "D": {"val": 2, "occ": 3},
        "E": {"val": 1, "occ": 15},
        "F": {"val": 4, "occ": 2},
        "G": {"val": 2, "occ": 2},
        "H": {"val": 4, "occ": 2},
        "I": {"val": 1, "occ": 8},
        "J": {"val": 8, "occ": 1},
        "K": {"val": 10, "occ": 1},
        "L": {"val": 1, "occ": 5},
        "M": {"val": 2, "occ": 3},
        "N": {"val": 1, "occ": 6},
        "O": {"val": 1, "occ": 6},
        "P": {"val": 3, "occ": 2},
        "Q": {"val": 8, "occ": 1},
        "R": {"val": 1, "occ": 6},
        "S": {"val": 1, "occ": 6},
        "T": {"val": 1, "occ": 6},
        "U": {"val": 1, "occ": 6},
        "V": {"val": 4, "occ": 2},
        "W": {"val": 10, "occ": 1},
        "X": {"val": 10, "occ": 1},
        "Y": {"val": 10, "occ": 1},
        "Z": {"val": 10, "occ": 1},
        "?": {"val": 0, "occ": 2}
    }

# Cette fonction renvoie une liste contenant tous les mots autorisés au scrabble
def generer_dico(nf):
    mots_autorise = []
    fichier = open(nf, "r").readlines()
    for ligne in fichier:
        mots_autorise.append(ligne.upper().replace("\n", ""))

    return mots_autorise

# Cette fonction initialise la pioche en y ajoutant le nombre requis de chaque lettre
def init_pioche(dico_valeur):
    pioche = []
    for lettre in dico_valeur:
        for x in range(dico_valeur[lettre]["occ"]):
            pioche.append(lettre)
    return pioche

# Initialise les cases bonus du plateau de jeu
def init_bonus():
    ligne_bonus = [""] * 15
    liste_bonus = []
    for i in range(15):
        liste_bonus.append(list(ligne_bonus))

    cases_MT = [[0, 0], [0, 7], [0, 14], [7, 0], [7, 14], [14, 0], [14, 7], [14, 14]]
    cases_MD = [[1, 1], [1, 13], [2, 2], [2, 12], [3, 3], [3, 11], [4, 4], [4, 10], [7, 7], [10, 4], [10, 10], [11, 3],
                [11, 11], [12, 2], [12, 12], [13, 1], [13, 13]]
    cases_LT = [[1, 5], [1, 9], [5, 1], [5, 5], [5, 9], [5, 13], [9, 1], [9, 5], [9, 9], [9, 13], [13, 5], [13, 9]]
    cases_LD = [[0, 3], [0, 11], [2, 6], [2, 8], [3, 0], [3, 7], [3, 14], [6, 2], [6, 6], [6, 8], [6, 12], [7, 3],
                [7, 11], [8, 2], [8, 6], [8, 8], [8, 12], [11, 0], [11, 7], [11, 14], [12, 6], [12, 8], [14, 3],
                [14, 11]]
    for x in cases_MT:
        liste_bonus[x[0]][x[1]] = "McT"
    for x in cases_MD:
        liste_bonus[x[0]][x[1]] = "McD"
    for x in cases_LT:
        liste_bonus[x[0]][x[1]] = "LcT"
    for x in cases_LD:
        liste_bonus[x[0]][x[1]] = "LcD"
    return liste_bonus


# Initialise le plateau de jeu (vierge)
def init_jetons():
    ligne_vierge = [" "] * 15
    liste_jetons = []
    for i in range(15):
        liste_jetons.append(list(ligne_vierge))
    return liste_jetons


# Affiche dans la console le plateau de jeu avec les lettres déjà posées et les bonus
def affiche_jetons(liste):

    liste_bonus_affich = init_bonus()
    ligne = 0
    plateau_str = "   |  " + "  |  ".join(str(item + 1) for item in range(9)) + "  | " + "  | ".join(
        str(item + 1) for item in range(9, 15)) + "  |"
    plateau_str += "\n----------------------------------------------------------------------------------------------\n"

    while ligne < 15:
        if ligne < 9:
            plateau_str += " " + str(ligne + 1) + " |"
        else:
            plateau_str += " " + str(ligne + 1) + "|"
        for i in range(15):
            if len(liste_bonus_affich[ligne][i]) == 3 and liste[ligne][i] == " ":
                plateau_str += " " + liste_bonus_affich[ligne][i] + " |"
            elif liste[ligne][i] != " ":
                if liste_bonus_affich[ligne][i] == "LcD":
                    plateau_str += " +" + liste[ligne][i] + "+ |"
                elif liste_bonus_affich[ligne][i] == "LcT":
                    plateau_str += " *" + liste[ligne][i] + "* |"
                elif liste_bonus_affich[ligne][i] == "McD":
                    plateau_str += " ~" + liste[ligne][i] + "~ |"
                elif liste_bonus_affich[ligne][i] == "McT":
                    plateau_str += " °" + liste[ligne][i] + "° |"
                else:
                    plateau_str += "  " + liste[ligne][i] + "  |"
            else:
                plateau_str += "     |"
        plateau_str += "\n----------------------------------------------------------------------------------------------\n"
        ligne += 1

    plateau_str += "Legende : '+' = LcD | '*' = LcT | '~' = McD | '°' = McT"
    plateau_str += "\n----------------------------------------------------------------------------------------------\n"

    return plateau_str

# Renvoie la liste de tous les mots du plateau. Si le paramètre all = 1 la fonction renvoie aussi les lettres seules
def mots_plateau(plateau, all=0):
    liste_mots_plateau = []

    if all != 0:
        all = 1

    # Renvoie la liste des mots sur les lignes du plateau ainsi que la ligne ou il a été trouvé
    for ligne in range(15):
        mots_plateau_ligne_espace = "".join(plateau[ligne])  # str
        liste_mots = mots_plateau_ligne_espace.split(" ")

        for mot in liste_mots:
            if len(mot) >= 2 - all and mot != " ":
                liste_mots_plateau.append([mot, ligne, "droite"])

    # Renvoie la liste des mots sur les colonnes du plateau ainsi que la colonne ou il a été trouvé
    for colonne in range(15):
        mots_plateau_colonne_espace = "".join(plateau[z][colonne] for z in range(15))
        liste_mots = mots_plateau_colonne_espace.split(" ")

        for mot in liste_mots:
            if len(mot) >= 2 - all and mot != " ":
                liste_mots_plateau.append([mot, colonne, "bas"])

    return liste_mots_plateau

# Cette fonction teste si le placement d'un mot respecte les règles du scrabble
def tester_placement_mot(plateau, coords, dirctn, mot, liste_main, motsfr):

    # Verifie que le mot ne sort pas du plateau
    if (dirctn == "bas" and (coords[0] + len(mot) - 1) > 14) or (
            dirctn == "droite" and (coords[1] + len(mot) - 1) > 14):
        return False, "Mot hors plateau"

    # Crée une chaine de caractère mettant en evidence les lettres deja posées qui sont sur le chemin du mot
    lettre_sur_tableau = ""
    lettre_necessaires = ""
    test_plateau = copy.deepcopy(plateau)
    placer_mot(test_plateau, mot, coords, dirctn)

    if dirctn == "droite":
        for i in range(len(mot)):
            if plateau[coords[0]][coords[1] + i] == " ":
                lettre_sur_tableau += " "
            else:
                lettre_sur_tableau += plateau[coords[0]][coords[1] + i]
    elif dirctn == "bas":
        for i in range(len(mot)):
            if plateau[coords[0] + i][coords[1]] == " ":
                lettre_sur_tableau += " "
            else:
                lettre_sur_tableau += plateau[coords[0] + i][coords[1]]
    else:
        return False, "Direction invalide"

    # Vérifie à l'aide de la chaine de caractère créé précédemment que les lettres déjà posées sur le plateau
    # n'entrent pas en conflit avec le mot
    conflit=True
    for i in range(len(mot)):
        if lettre_sur_tableau[i] == " ":
            lettre_necessaires += mot[i]
        elif lettre_sur_tableau[i] != mot[i]:
            conflit=False

    # Vérifie que le joueur à les lettres nécessaires dans sa main pour poser le mot
    if not IA.mot_jouable(lettre_necessaires, liste_main)[0]:
        return False, "Vous n'avez pas les lettres nécessaires"
    
    # On test conflit ici car l'erreur précédente est plus importante et doit être testée avant
    if not conflit:
        return False, "Le mot est en conflit avec une lettre déjà posée"

    
    # Verifie que le mot passe par la case du milieu si c'est le premier round
    if plateau[7][7] == " ":
        if test_plateau[7][7] == " ":
            return False, "Le premier mot doit passer par la case du milieu"

    # Teste si un mot n'est pas entièrement sur un mot deja placé sur la plateau
    if lettre_sur_tableau == mot:
        return False, "Vos lettres ne créent aucun nouveau mot"


    # Vérifie que le mot est connecté a un autre mot déjà posé sur le plateau
    mots_plateau_avant = list(mots_plateau(plateau)[x][0] for x in range(len(mots_plateau(plateau))))
    mots_plateau_apres = list(mots_plateau(test_plateau)[x][0] for x in range(len(mots_plateau(test_plateau))))

    if lettre_sur_tableau == len(mot) * " " and valeur_plateau(mots_plateau_apres) == valeur_plateau(
            mots_plateau_avant) + valeur_mot(mot) and valeur_plateau(mots_plateau_avant) > 0:
        return False, "Le mot doit etre connecté à un autre mot du plateau"

    # Vérifie que les mots crées à partir du mot pose sont bien dans le dictionnaire du Scrabble
    for mot in mots_plateau(test_plateau):
        if mot[0] not in motsfr:
            return False, "Le mot ne coincide pas avec les autres"

    

    return True, lettre_necessaires


# Cette fonction peut placer un mot sur le tableau et modifier le sac et la main du joueur si le paramètre modif_main = 1
def placer_mot(plateau, mot, coords, dirctn, ltr_necessaire=None, liste_main=None, sac=None, modif_main=0):
    
    # Place le mot sur le tableau
    if dirctn == "droite":
        for i in range(len(mot)):
            plateau[coords[0]][coords[1] + i] = mot[i]

    if dirctn == "bas":
        for i in range(len(mot)):
            plateau[coords[0] + i][coords[1]] = mot[i]

    # Ajuste la main du joueur et la pioche en fonction du mot
    if modif_main == 1:
        ltr_necessaire = list(ltr_necessaire)

        for lettre in ltr_necessaire:
            if lettre in liste_main:
                liste_main.remove(lettre)
            else:
                liste_main.remove("?")

        jo.completer_main(liste_main, sac)

# Calcule le score d'un mot en fonction ou pas des bonus selon la valeur de multip (par defaut sans les bonus = 0)
# Le paramètre modif bonus permet ou pas de déclarer une case bonus ocupée
def valeur_mot(mot, coords=None, dirctn=None, grille_bonus=None, multip=0, modif_bonus=1, dico_valeur=init_dico()):
    mot = list(mot)
    points = 0
    coeff = 1

    # Calcule le score d'un mot en appliquant les bonus corespondant
    if multip != 0:
        for i in range(len(mot)):
            if dirctn == "droite":
                ligne = 0
                colonne = i
            else:
                ligne = i
                colonne = 0
            if grille_bonus[coords[0] + ligne][coords[1] + colonne] == "":
                points += dico_valeur[mot[i]]["val"]
            elif grille_bonus[coords[0] + ligne][coords[1] + colonne] == "McD":
                points += dico_valeur[mot[i]]["val"]
                coeff *= 2
            elif grille_bonus[coords[0] + ligne][coords[1] + colonne] == "McT":
                points += dico_valeur[mot[i]]["val"]
                coeff *= 3
            elif grille_bonus[coords[0] + ligne][coords[1] + colonne] == "LcD":
                points += dico_valeur[mot[i]]["val"] * 2
            elif grille_bonus[coords[0] + ligne][coords[1] + colonne] == "LcT":
                points += dico_valeur[mot[i]]["val"] * 3
            if modif_bonus != 0:
                grille_bonus[coords[0] + ligne][coords[1] + colonne] = ""

    # Calcule le score brut d'un mot (sans les bonus)
    else:
        for lettre in mot:
            points += dico_valeur[lettre]["val"]
    return points * coeff

# Renvoie la valeur brute de tous les mots du plateau
def valeur_plateau(lmp):
    points = 0
    for mot in lmp:
        points += valeur_mot(mot)
    return points

# Cette fonction permet d'actualiser le mot de l'utilisateur si le mot qu'il place crée directement un autre mot
# et ajuste les coordonées en fonction. Exemple : Si le joueur place CHANGE à droite d'un E le mot sera actualisé
# en ECHANGE et les coordonnées seront actualisées sur le premier E
def mot_cree(mot_uti, plateau, direction, coords):

    plateau_test = copy.deepcopy(plateau)
    placer_mot(plateau_test, mot_uti, coords, direction)
    nouveau_mot = mot_uti

    if direction == "droite":
        liste_ligne = "".join(plateau_test[coords[0]]).split(" ")
        for mot in liste_ligne:
            if mot_uti in mot:
                caracteres_en_plus = mot.replace(mot_uti, "", 1)              
                nouveau_mot = mot
                if nouveau_mot != mot_uti + caracteres_en_plus:
                    coords[1] -= len(caracteres_en_plus)
    else:
        liste_colonne = "".join(plateau_test[ligne][coords[1]] for ligne in range(15)).split(" ")
        for mot in liste_colonne:
            if mot_uti in mot:
                caracteres_en_plus = mot.replace(mot_uti, "", 1)
                nouveau_mot = mot
                if nouveau_mot != mot_uti + caracteres_en_plus:
                    coords[0] -= len(caracteres_en_plus)

    return nouveau_mot, coords

# Renvoie l'élement correspondant au score par chaque longueur de liste
def filtre(elem):
    if len(elem)==5:
        return elem[4]
    elif len(elem)==3:
        return elem[2]
    else:
        return elem[1]

# Cette fonction renvoie le score d'un coup (score du mot avec bonus + eventuels mots crés + 50 si 7 lettres jouées)
# Le paramètre modif bonus permet ou pas de déclarer une case bonus ocupée
def calculer_score(plateau, ancien_plateau, mot_uti, coordonnees, dirctn, bonus, lettre_necessaires, modif_bonus=1):
    score = 0

    # Calcule le score du mot en prenant en compte les éventuels bonus et l'ajoute au score du joueur
    score += valeur_mot(mot_uti, coordonnees, dirctn, bonus, 1, modif_bonus)

    # Calcule le score des nouveaux mots crées suite au placement du mot et l'ajoute au score du joueur
    liste_mots_avant = list(mots_plateau(ancien_plateau)[x][0] for x in range(len(mots_plateau(ancien_plateau))))
    liste_mots_apres = list(mots_plateau(plateau)[x][0] for x in range(len(mots_plateau(plateau))))

    for mot in liste_mots_avant:
        if mot in liste_mots_apres:
            liste_mots_apres.remove(mot)

    liste_mots_apres.remove(mot_uti)

    for mot in liste_mots_apres:
        score += valeur_mot(mot)

    if len(lettre_necessaires) == 7:
        score += 50

    return score