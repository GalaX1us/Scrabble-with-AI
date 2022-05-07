from random import *
import copy
from json import *
import time
import plateau as plat
import joueur as jo
import IA

# Renvoie True si une chaine de caractères peut etre crée a partir des lettres de la main d'un joueur
def mot_jouable(mot_ch, ll, nb_lettre_manquante=0):
    
    ll_test = list(ll)
    possible = True
    nb_erreurs = 0
    mot = list(mot_ch.upper())

    for ch in mot:
        if ch in ll_test:
            ll_test.remove(ch)
        else:
            nb_erreurs += 1

    # Renvoie False si le nombres d'incohérences (tolérence ajustée si besoin par le paramètre
    # nb_lettre_manquante) est superieur au nombre de joker du joueur

    if nb_erreurs - nb_lettre_manquante > ll_test.count("?"):
        possible = False

    return possible, nb_erreurs - nb_lettre_manquante


# Cette fonction renvoie la liste des mots jouables avec les lettres du joueur et en fonction d'une contrainte de
# chaine de caractères. Par exemple tous les mots possible contenant la chaine de caractères "ais" et pouvant être
# completés avec les lettres de la main du joueur. S'il n'y a pas de contrainte elle renvoie tous les mots possible
# avec la main du joueur
def mots_jouables(ll, motsfr, contrainte="",
                  nb_lettre_manquante=0, renvoie_lettre_necessaires=0):

    jouables = []
    for mot in motsfr:
        if contrainte in mot:
            mot_test = mot.replace(contrainte, "", 1)
            if mot_jouable(mot_test, ll, nb_lettre_manquante)[0] and mot_test!="":

                # si renvoie_lettre_necessaires = 0 renvoie juste le mot
                if renvoie_lettre_necessaires == 0:
                    jouables.append([mot, plat.valeur_mot(mot) ])
                else:
                    jouables.append([mot, mot_test, plat.valeur_mot(mot)])  # Sinon renvoie le mot et les lettres necessaires pour le faire

    return jouables


# Renvoie la liste de les mots possible à partir de la main du joueur et des lettres déjà placées sur le plateau ainsi
# que des infos sur leur positions possible
def mots_plateau_main(liste_main, plateau, motsfr, mots_deja_place):

    # Donne la liste des colonne et des lignes sur lesquelles les mots de la main doivent être testés
    # Renvoie la liste des lignes et des colonnes adjacents aux mots déjà posés
    liste_ligne_colonne=[]
    if plateau[7][7]==" ":
        liste_ligne_colonne=[[7,"droite"],[7,"bas"]]
    for mot in mots_deja_place:
        
        # Ajoute à la liste les lignes adjacentes au mot
        if mot[2]=="droite":
            if mot[1][0]+1<15 and [mot[1][0]+1, "droite"] not in liste_ligne_colonne:
                liste_ligne_colonne.append([mot[1][0]+1, "droite"])
            elif mot[1][0]-1>=0 and [mot[1][0]-1, "droite"] not in liste_ligne_colonne:
                liste_ligne_colonne.append([mot[1][0]-1, "droite"])
            
            # Ajoute à la liste les colonne perpendiculaires aux extrémités du mot
            if mot[1][1]-1>=0 and [mot[1][1]-1, "bas"] not in liste_ligne_colonne:
                liste_ligne_colonne.append([mot[1][1]-1, "bas"])
            elif mot[1][1]+len(mot[0])<15 and [mot[1][1]+len(mot[0]), "bas"] not in liste_ligne_colonne:
                liste_ligne_colonne.append([mot[1][1]+len(mot[0]), "bas"])
        else:
            # Ajoute à la liste les colonnes adjacentes au mot
            if mot[1][1]+1<15 and [mot[1][1]+1, "bas"] not in liste_ligne_colonne:
                liste_ligne_colonne.append([mot[1][1]+1, "bas"])
            elif mot[1][1]-1>=0 and [mot[1][1]-1, "bas"] not in liste_ligne_colonne:
                liste_ligne_colonne.append([mot[1][1]-1, "bas"])
            
            # Ajoute à la liste les lignes perpendiculaires aux extrémités du mot
            if mot[1][0]-1>=0 and [mot[1][0]-1, "droite"] not in liste_ligne_colonne:
                liste_ligne_colonne.append([mot[1][0]-1, "droite"])
            elif mot[1][0]+len(mot[0])<15 and [mot[1][0]+len(mot[0]), "droite"] not in liste_ligne_colonne:
                liste_ligne_colonne.append([mot[1][0]+len(mot[0]), "droite"])

    # Initialise la liste de mots possibles avec la liste de mots possible avec la main du joueur.
    liste_mots = mots_jouables(liste_main, motsfr, renvoie_lettre_necessaires=1)
    
    # Donne la liste de tous les mots du plateau y compris les caractères seuls
    liste_lettre = list(liste_main)
    liste_mots_plateau = plat.mots_plateau(plateau, 1)
    
    # Teste si des mots sont possibles à partir d'un des mots ou caractère déja posé sur le plateau
    if len(liste_mots_plateau) > 0:
        for mots in liste_mots_plateau:
            liste_jouable = mots_jouables(liste_lettre, motsfr ,contrainte=mots[0], renvoie_lettre_necessaires=1)
            if len(liste_jouable) > 0:
                for mot in liste_jouable:
                    # if mot[0] not in (liste_mots[x][0] for x in range(len(liste_mots))):

                        # On garde les lettres necessaires pour améliorer la proposition de mot plus tard
                    liste_mots.append(
                        [mot[0], mot[1], mots[1],
                            mots[2], mot[2]])  # [Mot / Lettres necessaires / numéro ligne ou colonne / direction / valeur brute]
    
    return liste_mots, liste_ligne_colonne


# Renvoie la liste des mots posable sur le tableau parmi les mots donnés et leurs infos de placement
# infos_mot est soit égale à [Mot / Lettres necessaires / numéro ligne ou colonne ou l'élément doit être testé / direction / valeur brut]
# soit à [Mot / Lettres necessaires / valeur brut] et est testé différement l'un de l'autre
def mot_posable(infos_mot, plateau, liste_main, motsfr, liste_ligne_colonne):
    resultat = []

    # Test les emplacements possibles d'un mot sur une seule ligne ou colonne donnée 
    if len(infos_mot) > 3:
        if infos_mot[3] == "droite":
            for colonne in range(15):
                check = plat.tester_placement_mot(plateau, [infos_mot[2], colonne], "droite",infos_mot[0], liste_main, motsfr)
                if check[0]:
                    nouvelle_infos = plat.mot_cree(infos_mot[0], plateau, "droite", [infos_mot[2], colonne])
                    resultat.append([nouvelle_infos[0], nouvelle_infos[1], "droite",
                                     check[1]])
        else:
            for ligne in range(15):
                check = plat.tester_placement_mot(plateau, [ligne, infos_mot[2]], "bas", infos_mot[0], liste_main, motsfr)
                if check[0]:
                    nouvelle_infos = plat.mot_cree(infos_mot[0], plateau, "bas", [ligne, infos_mot[2]])
                    resultat.append([nouvelle_infos[0], nouvelle_infos[1], "bas",
                                     check[1]])

    else:
        for pos in liste_ligne_colonne:
            # Ajoute a la liste de resultat tous les mots posable HORIZONTALEMENT sur le tableau parmi les mots donnés et
            # leurs infos
        
            if pos[1] == "droite":
                for colonne in range(15):
                    check = plat.tester_placement_mot(plateau, [pos[0], colonne], "droite", infos_mot[0], liste_main, motsfr)
                    if check[0]:
                        nouvelle_infos = plat.mot_cree(infos_mot[0], plateau, "droite", [pos[0], colonne])
                        resultat.append([nouvelle_infos[0], nouvelle_infos[1], "droite",
                                     check[1]])
            else:
                for ligne in range(15):
                    check = plat.tester_placement_mot(plateau, [ligne, pos[0]], "bas", infos_mot[0], liste_main, motsfr)
                    if check[0]:
                        nouvelle_infos = plat.mot_cree(infos_mot[0], plateau, "bas", [ligne, pos[0]])
                        resultat.append([nouvelle_infos[0], nouvelle_infos[1], "bas",
                                     check[1]])
    return resultat  # Renvoie le mot qui va être posé sur le plateau / ses coordonnées / sa direction / les lettres nécessaires

# Trie la liste donnée en paramètre en les classant en fonction de leur potentiel
def mots_fort_potentiel(liste_infos_mots):
    
    # Trie les mots de la liste en fonction de leur score brut
    liste_infos_mots.sort(key=plat.filtre, reverse=True)
    liste_sept=[]

    # Sort de la liste des mots possibles les mots nécessitants 7 lettres et les trie entre eux en fonction de leur score
    for mot in liste_infos_mots:
        if len(mot[1])==7:
            liste_infos_mots.remove(mot)
            liste_sept.append(mot)
    liste_sept.sort(key=plat.filtre)
    
    # Ajoute la liste triée des mots de 7 à la liste de départ
    for mot in liste_sept:
        liste_infos_mots.insert(0 ,mot)       


# Cette fonction renvoie le mot posable ayant le score le plus élevé
#
# Fiable à 99% car teste seulement les mots à fort potentiel (pour améliorer les perfs)
# PS : j'ai indiqué 99% car dans l'absolu ce n'est pas le meilleur mot parmi tous ceux posables,
# mais en ayant effectué beaucoup de test il s'avère que le meilleur mot posable absolu était le même que celui renvoyé par cette fonction
#
# La fonction compare les 30 premiers mots ayant le plus de potentiel puis, 
# si aucun n'est posable renvoie le premier posable sachant que les mots sont triés par potentiel
def meilleur_mot_posable(liste_main, plateau, bonus, motsfr, mots_deja_place):
    
    infos_mots = mots_plateau_main(liste_main, plateau, motsfr, mots_deja_place)
    mots=infos_mots[0]
    liste_ligne_colonne=infos_mots[1]
    mots_fort_potentiel(mots)

    meilleur_mot = ""
    meilleur_score = 0

    if len(mots)>30:
        maxi=30
    else:
        maxi=len(mots)
    
    # Teste quel est le meilleur placement parmi les 30 mots ayant le plus de potentiel
    for indice in range(0,maxi):
        mot=mots[indice]
        liste_mots_posable = mot_posable(mot, plateau, liste_main, motsfr, liste_ligne_colonne)

        for info_mot in liste_mots_posable:
            plateau_test = copy.deepcopy(plateau)
            plat.placer_mot(plateau_test, info_mot[0], info_mot[1], info_mot[2])
            score_mot = plat.calculer_score(plateau_test, plateau, info_mot[0], info_mot[1], info_mot[2], bonus, info_mot[3],
                                       modif_bonus=0)

            # Teste le score de chaque mot en fonction de son placement et renvoie celui ayant le plus grand
            if score_mot > meilleur_score:
                meilleur_score = score_mot
                meilleur_mot = info_mot
                meilleur_mot.append(score_mot)
           
    # Renvoie le premier mot posable dans l'ordre de ceux les plus propices
    if meilleur_mot == "" and maxi!=len(mots):
        for indice in range(maxi,len(mots)):
            mot=mots[indice]
            liste_mots_posable = mot_posable(mot, plateau, liste_main, motsfr, liste_ligne_colonne)

            for info_mot in liste_mots_posable:
                plateau_test = copy.deepcopy(plateau)
                plat.placer_mot(plateau_test, info_mot[0], info_mot[1], info_mot[2])
                score_mot = plat.calculer_score(plateau_test, plateau, info_mot[0], info_mot[1], info_mot[2], bonus, info_mot[3],
                                        modif_bonus=0)

                # Teste le score de chaque mot en fonction de son placement et renvoie celui ayant le plus grand
                if score_mot > meilleur_score:
                    meilleur_score = score_mot
                    meilleur_mot = info_mot
                    meilleur_mot.append(score_mot)
            
            if meilleur_mot!="":
                return meilleur_mot

    # Renvoie False si aucun mots n'est posable    
    if meilleur_mot == "":
        return False
    
    return meilleur_mot


# Renvoie le nombre de consonnes et de voyelles d'une chaine de caractères
# Elle n'est pas utile pour le moment mais pourrait l'être pour améliorer le choix des mots dans l'aide
def conssonnes_voyelle(ll):
    voyelles = 0
    consonnes = 0
    for lettre in ll:
        if lettre in "AEIOUY":
            voyelles += 1
        else:
            consonnes += 1
    return voyelles, consonnes


# Renvoie les infos d'un mots choisi aléatoirement parmi tout ceux posable
def proposition_mot_posable(liste_main, plateau, motsfr, mots_deja_place):

    # Choisi un mot aleatoirement parmi tout ceux possible à partir de notre main et des jetons deja posés sur le
    # plateau
    infos_mots = mots_plateau_main(liste_main, plateau, motsfr, mots_deja_place)
    mots=infos_mots[0]
    liste_ligne_colonne=infos_mots[1]

    if len(mots) == 0:
        return False

    
    mot_alea = choice(mots)

    # Test si le mot choisi ci-dessus est posable quelque part sinon en choisi un autre
    while mot_posable(mot_alea, plateau, liste_main, motsfr, liste_ligne_colonne) == [] and len(mots) > 1:
        mots.remove(mot_alea)
        mot_alea = choice(mots)

    if mot_posable(mot_alea, plateau, liste_main, motsfr, liste_ligne_colonne) == []:
        mots.remove(mot_alea)

    # Si pas de mot posable return False
    if len(mots) == 0:
        return False

    possibilite = mot_posable(mot_alea, plateau, liste_main, motsfr, liste_ligne_colonne)
    resulat_alea = possibilite[randint(0, len(possibilite) - 1)]

    return resulat_alea