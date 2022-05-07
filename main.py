from random import *
import copy
from json import *
import time
import plateau as plat
import joueur as jo
import IA

# Cette fonction demande des coordonnées jusqu'à ce qu'elles soit valide
def lire_coords():
    print(
        "\nQuelles sont les coordonees de la case de votre premiere lettre (votre mot se placera a droite ou en bas)\n")

    # Demande les coordonnées du mot à l'utilisateur jusqu'a ce qu'elles soit entre 1 et 15 compris et verifie
    # que ce sont bien de chiffres

    x, y = -1, -1
    while not 1 <= x <= 15 or not 1 <= y <= 15:
        x, y = input("Coordonee X (colonne entre 1 et 15) :"), input("Coordonee Y (ligne entre 1 et 15) :")
        try:
            x, y = int(x), int(y)
        except ValueError:
            print("Vous n'avez pas saisi de nombre")
            x, y = -1, -1
    coords = [int(y) - 1, int(x) - 1]
    return coords



# Cette fonction demande les informations nécessaires au placement d'un mot à l'utilisateur jusqu'à ce qu'elles soit
# valide
def lire_mot(plateau, liste_main, motsfr):

    # Demande a l'utilisateur quel mot il veut jouer et verifie qu'il est bien dans le dictionnaire
    mot_uti = input(
        "\nQuel mot voulez vous jouer ? (ne rien mettre pour passer son tour et changer de main) : ").upper()

    while mot_uti not in motsfr and mot_uti != "":
        print("Mot invalide")
        mot_uti = input(
            "Quel mot voulez vous jouer ? (ne rien mettre pour passer son tour et changer de main) : ").upper()
    if mot_uti == "":
        return "PASSE_TOUR"

    # Demande les coordonnees de la premiere lettre du mot
    coordonnees = lire_coords()

    # Demande la direction et vérfie que celle-ci est valide
    direction = input("\nDans quel direction (droite ou bas) : ").lower()
    while direction != "droite" and direction != "bas":
        print("Direction invalide")
        direction = input("Dans quel direction (droite ou bas) : ").lower()

    nouvelle_infos = plat.mot_cree(mot_uti, plateau, direction, coordonnees)
    mot_uti, coordonnees = nouvelle_infos[0], nouvelle_infos[1]

    check = plat.tester_placement_mot(plateau, coordonnees, direction, mot_uti, liste_main, motsfr)
    if not check[0]:
        print("\nErreur : {}".format(check[1]))
        return lire_mot(plateau, liste_main, motsfr)

    return mot_uti, coordonnees, direction, check[1]





# Cette fonction gère les aides mis à disposition du joueur
def besoin_aide(liste_main, plateau, bonus, motsfr, mots_deja_place):

    # Demande à l'utilisateur quel type d'aide il veut
    choix = input("Quel type d'aide voulez vous (1 : mot aleatoire, 2 : meilleur mot) : ")

    while choix != "1" and choix != "2":  # Verifie que le cchoix du joueur fait partie des choix proposés
        print("Choix invalide")
        choix = input("Quel type d'aide voulez vous (1 : mot aleatoire, 2 : meilleur mot) : ")

    # Renvoie toutes les infos d'un mot posable par le joueur sur le plateau (mot, coordonnées et direction)
    if choix == "1":
        mot_aide = IA.proposition_mot_posable(liste_main, plateau, motsfr, mots_deja_place)

        # Inverse les coordonnées et leurs ajoute 1 car dans notre jeu le plateau commence à 1 et demande la colonne
        # en premier
        mot_aide[1][0], mot_aide[1][1] = mot_aide[1][1] + 1, mot_aide[1][0] + 1

        if mot_aide != False:
            print("\nA partir de votre main vous pouvez faire le mot {} en {} vers le/la {}".format(mot_aide[0],
                                                                                                    mot_aide[1],
                                                                                                    mot_aide[2]))
        else:
            print("A partir de votre main vous ne pouvez rien faire")

    # Renvoie les informations sur le meilleur mot posable
    if choix == "2":
        mot_aide = IA.meilleur_mot_posable(liste_main, plateau, bonus, motsfr, mots_deja_place)

        # Inverse les coordonnées et leurs ajoute 1 car dans notre jeu le plateau commence à 1 et demande la colonne
        # en premier
        mot_aide[1][0], mot_aide[1][1] = mot_aide[1][1] + 1, mot_aide[1][0] + 1

        if mot_aide != False:
            print(
                "\nA partir de votre main et du plateau le meilleur mot possible est {} en {} vers le/la {} avec un score de {}".format(
                    mot_aide[0], mot_aide[1], mot_aide[2], mot_aide[4]))

        else:
            print("A partir de votre main vous ne pouvez rien faire")





# Cette fonction permet de sauvegarder les informations de jeu actuelles pour continuer la partie plus tard
def sauvegarder(num_round, infos, plateau, sac, bonus, tours_passe_consecutif, dico, mots_deja_place, duree_partie, choix_option_dev=None):

    # Sauvegarde toutes les informations nécessaires à la poursuite ultérieure de la partie dans un fichier json
    # (une seule sauvegarde possible a la fois, sinon la précedente sauvegarde est écrasée)

    if len(dico)>100000:
        dico="OFFICIEL.txt"
    else:
        dico="COMPACT.txt"
    
    sauvegarder_infos = [num_round, infos, plateau, sac, bonus, tours_passe_consecutif, dico, mots_deja_place, round(duree_partie), choix_option_dev]
    with open('save.json', 'w') as fichier:
        dump(sauvegarder_infos, fichier)


# Détermine et affiche les stats de la parties
def statistiques(infos_joueurs, num_round):
    
    global duree_partie

    classement = []

    # Classe les joueurs en fonctions de leur score
    for x,y in sorted(infos_joueurs.items(), key=lambda x: x[1]["score"], reverse=True):
            classement.append(y)

    print("\n============")
    print("Statistiques")
    print("============")
    print("\nLa partie s'est deroulée sur {} rounds en {}min {}sec !".format(num_round-1, duree_partie//60, duree_partie%60))

    # Affiche le classement et les stats
    print("\nBien joué a {} qui remporte la VICTOIRE avec {} points !!!".format(classement[0]["pseudo"], classement[0]["score"]))
    print("Son meilleur coup est le mot {} qui lui a rapporté {} points !".format(classement[0]["stat"][1],
                                                                                      classement[0]["stat"][0]))
    for podium in range(len(classement) - 1):
        print("\nBien joué a {} qui remporte la {}éme place avec {} points !!!".format(classement[podium + 1]["pseudo"],
                                                                                           podium + 2,
                                                                                           classement[podium + 1]["score"]))
        print("Son meilleur coup est le mot {} qui lui a rapporté {} points !".format(classement[podium + 1]["stat"][1],
                                                                                          classement[podium + 1]["stat"][0]))


# Cette fonction gères les actions à effectuer durant le tour du joueur
def tour_joueur(plateau, infos_joueurs, sac, bonus, finit, tours_passe_consecutif, num_round, motsfr, mots_deja_place):

    global duree_partie

    # Définit le joueur actuel

    joueur_actuel = infos_joueurs[str((num_round - 1) % len(infos_joueurs))]

    if finit[0] == 0 and tours_passe_consecutif < len(infos_joueurs)*3:  # test si c'est la fin de la partie
        # Affiche les infos essentielles au le joueur

        print("\nRound n°{} : {}".format(num_round, joueur_actuel["pseudo"]) + "\n")
        print(plat.affiche_jetons(plateau))
        print("Voici votre main : " + jo.afficher_main(
            joueur_actuel["main"]) + "     Pieces restantes dans le sac : {}".format(len(sac)) + "\n")

        # Fait jouer l'IA et passe au tour d'après

        if joueur_actuel["IA"] == "OUI":
            if joueur_actuel["diff"] == "NORMALE":
                # Choisi aléatoirement le mot que l'IA va jouer
                mot_aide = IA.proposition_mot_posable(joueur_actuel["main"], plateau, motsfr, mots_deja_place)
            else:
                mot_aide = IA.meilleur_mot_posable(joueur_actuel["main"], plateau, bonus, motsfr, mots_deja_place)

            if not mot_aide:

                # Change la main de l'IA aucun mot n'est possible à partir de sa main
                print("A partir de votre main vous ne pouvez rien faire")
                jo.echanger(joueur_actuel["main"], joueur_actuel["main"], sac)
                print("\nVotre nouvelle main est : " + jo.afficher_main(joueur_actuel["main"]))
                tours_passe_consecutif += 1

            else:
                coordonnees_inverse = [mot_aide[1][1] + 1, mot_aide[1][0] + 1]

                # Place le mot de l'IA et ajuste son score en fonction  et affcihe les actions effectuées
                plateau_avant = copy.deepcopy(plateau)
                plat.placer_mot(plateau, mot_aide[0], mot_aide[1], mot_aide[2], mot_aide[3], joueur_actuel["main"], sac, 1)
                valeur_du_coup = plat.calculer_score(plateau, plateau_avant, mot_aide[0], mot_aide[1],
                                                mot_aide[2],
                                                bonus, mot_aide[3])

                print("{} place le mot {} en {} vers le/la {} et gagne {} points".format(joueur_actuel["pseudo"],
                                                                                         mot_aide[0],
                                                                                         coordonnees_inverse,
                                                                                         mot_aide[2], valeur_du_coup))
                mots_deja_place.append([mot_aide[0], mot_aide[1], mot_aide[2]])
                # Actualise le meilleur coup de l'IA jusqu'à present
                joueur_actuel["score"] += valeur_du_coup
                if valeur_du_coup >= joueur_actuel["stat"][0]:
                    joueur_actuel["stat"] = [valeur_du_coup, mot_aide[0]]

                tours_passe_consecutif = 0
        # Fait jouer l'utilisateur
        else:
            # Laisse le choix à l'utilisateur entre plusieurs type d'extra
            choix_extra = input(
                "Extra : Voulez vous de l'aide ? (oui / non) ; sauvegarder (save) : ").upper()

            while choix_extra != "OUI" and choix_extra != "NON" and choix_extra != "SAVE":
                print("Choix invalide")
                choix_extra = input(
                    "Extra : Voulez vous de l'aide ? (oui / non) ; sauvegarder (save) : ").upper()

            # Permet de recevoir de l'aide de la part du jeu
            if choix_extra == "OUI":
                besoin_aide(joueur_actuel["main"], plateau, bonus, motsfr, mots_deja_place)

            # Permet de sauvegarder les données de la partie en cours
            elif choix_extra == "SAVE":
                sauvegarder(num_round, infos_joueurs, plateau, sac, bonus, tours_passe_consecutif, motsfr, mots_deja_place, time.time()-duree_partie)
                
                print("\n======================")
                print("Sauvegarde effectuée !")
                print("======================")

                choix_extra = input(
                "Extra : Voulez vous de l'aide ? (oui / non)").upper()

                while choix_extra != "OUI" and choix_extra != "NON":
                    print("Choix invalide")
                    choix_extra = input(
                        "Extra : Voulez vous de l'aide ? (oui / non)").upper()

                # Permet de recevoir de l'aide de la part du jeu
                if choix_extra == "OUI":
                    besoin_aide(joueur_actuel["main"], plateau, bonus, motsfr, mots_deja_place)
            
            # Choix du mot ou changement de main
            choix_uti = lire_mot(plateau, joueur_actuel["main"], motsfr)

            # Change de main et passe directement au tour d'après
            if choix_uti == "PASSE_TOUR":
                lettre_a_changer = input("\nQuelles lettres voulez vous changer ? :").upper()

                # Verifie que le joueur a les lettres qu'il veut echanger
                check_echanger = jo.echanger(lettre_a_changer, joueur_actuel["main"],
                                          sac)
                while check_echanger:
                    print("Vous n'avez pas toutes ces lettres")
                    lettre_a_changer = input("Quelles lettres voulez vous changer ? :").upper()
                    check_echanger = jo.echanger(lettre_a_changer, joueur_actuel["main"], sac)
                print("\nVotre nouvelle main est : " + jo.afficher_main(joueur_actuel["main"]))
                tours_passe_consecutif += 1

            else:

                # Place le mot, ajuste le score de  l'utilisateur en fonction et affiche tout ca
                coordonnees_inverse = [choix_uti[1][1] + 1, choix_uti[1][0] + 1]
                plateau_avant = copy.deepcopy(plateau)
                plat.placer_mot(plateau, choix_uti[0], choix_uti[1], choix_uti[2], choix_uti[3], joueur_actuel["main"], sac,
                           1)
                valeur_du_coup = plat.calculer_score(plateau, plateau_avant, choix_uti[0], choix_uti[1],
                                                choix_uti[2],
                                                bonus, choix_uti[3])
                joueur_actuel["score"] += valeur_du_coup
                print("{} place le mot {} en {} vers le/la {} et gagne {} points".format(joueur_actuel["pseudo"],
                                                                                         choix_uti[0],
                                                                                         coordonnees_inverse,
                                                                                         choix_uti[2], valeur_du_coup))
                mots_deja_place.append([choix_uti[0], choix_uti[1], choix_uti[2]])
                # Actualise le meilleur coup du joueur jusqu'à present
                if valeur_du_coup >= joueur_actuel["stat"][0]:
                    joueur_actuel["stat"] = [valeur_du_coup, choix_uti[0]]

                tours_passe_consecutif = 0

        # Permet de dire si c'est la la fin de partie
        if len(joueur_actuel["main"]) == 0 and len(sac) == 0:
            finit = [1, joueur_actuel]

        # Passe au tour d'après
        num_round += 1
        print("\nLe score de {} est actuellement de : {}".format(joueur_actuel["pseudo"], joueur_actuel["score"]))
        time.sleep(1)
        tour_joueur(plateau, infos_joueurs, sac, bonus, finit, tours_passe_consecutif, num_round, motsfr, mots_deja_place)
    else:

        # Démarre la procédure de fin de partie

        fin_partie(infos_joueurs, tours_passe_consecutif, finit, num_round)


# Initialise les infos essentielles de la partie telles que la pioche, le plateau, le nombre de joueurs et leur nom
# etc ...
def debut_partie():

    global duree_partie, motsfr
    
    # Initialisation des variables essentielles
    dico_possible = ["COMPACT.txt", "OFFICIEL.txt"]
    num_round = 1
    plateau_jeu = plat.init_jetons()
    dico_valeur = plat.init_dico()
    plateau_bonus = plat.init_bonus()
    pioche = plat.init_pioche(dico_valeur)
    tours_passe_consecutif = 0
    mots_deja_place=[]
    print("=========================")
    print("Scrabble by BONADA Nathan")
    print("=========================\n")

    # Choix entre nouvelle partie et chargement d'une ancienne sauvegarde
    choix_partie = input(
        "Voulez vous commencer une nouvelle partie ou charger une sauvegarde ? (nouvelle / sauvegarde) : ").lower()
    while choix_partie != "nouvelle" and choix_partie != "sauvegarde":
        print("\nReponse invalide\n")
        choix_partie = input(
            "Voulez vous commencer une nouvelle partie ou charger une sauvegarde ? (nouvelle / sauvegarde):").lower()

    if choix_partie == "nouvelle":

        # Demande le dictionnaire que l'utilisateur veut utiliser
        choix_dico = input("\nQuel dictionnaire voulez vous utiliser (Officiel: 400k mots (diminue les performances) "
                           "/ Compact: 70k mots) : ").upper()
        while choix_dico != "OFFICIEL" and choix_dico != "COMPACT":
            print("Choix invalide")
            choix_dico = input(
                "Quel dictionnaire voulez vous utiliser (Officiel: 400k mots (diminue les performances) / Compact: "
                "70k mots) : ").upper()
        if choix_dico == "OFFICIEL":
            motsfr = plat.generer_dico(dico_possible[1])
        else:
            motsfr = plat.generer_dico(dico_possible[0])

        # Demande à l'utilisateur le nombre de joueurs qu'il souhaite
        nb_de_joueurs = -1
        while nb_de_joueurs < 2 or nb_de_joueurs > 4:
            nb_de_joueurs = input("\nMerci de donner le nombre de joueurs (2-4) : ")
            try:
                nb_de_joueurs = int(nb_de_joueurs)
            except ValueError:
                print("Vous n'avez pas saisi de nombre")
                nb_de_joueurs = -1

        # Demande à l'utilisateur le nombre d'IA qu'il souhaite parmi les joueurs
        nb_ia = -1
        while nb_ia < 0 or nb_ia > nb_de_joueurs:
            nb_ia = input("\nCombien voulez-vous d'IA parmi ces {} joueurs ? : ".format(nb_de_joueurs))
            try:
                nb_ia = int(nb_ia)
            except ValueError:
                print("Vous n'avez pas saisi de nombre")
                nb_ia = -1

        joueurs = {}
        for i in range(nb_de_joueurs):

            # Création de nouveaux joueurs et de leurs informations (numéro, pseudo , main, score, stats)
            if i + 1 <= (nb_de_joueurs - nb_ia):
                nom = input("\nQuel est le pseudo du joueur {} : ".format(i + 1))
                i = str(i)
                joueurs[i] = {"pseudo": nom}
                joueurs[i]["main"] = []
                jo.completer_main(joueurs[i]["main"], pioche)
                joueurs[i]["score"] = 0
                joueurs[i]["IA"] = "NON"
                joueurs[i]["stat"] = [0, "meilleur mot"]

            # Création de nouvelles IA et de leurs informations (numéro, pseudo , main, score, stats)
            else:
                nom = input("\nQuel est le pseudo de l'IA n°{} : ".format((i + 1) - (nb_de_joueurs - nb_ia)))
                diff = input("Quel est sa difficulté (normale / extreme) : ").upper()
                while diff != "NORMALE" and diff != "EXTREME":
                    print("Difficulté invalide")
                    diff = input("Quel est sa difficulté (normale / extreme) : ").upper()
                i = str(i)
                joueurs[i] = {"pseudo": nom + "(IA)"}
                joueurs[i]["main"] = []
                jo.completer_main(joueurs[i]["main"], pioche)
                joueurs[i]["score"] = 0
                joueurs[i]["IA"] = "OUI"
                joueurs[i]["stat"] = [0, "meilleur mot"]
                joueurs[i]["diff"] = diff
        duree_partie=time.time()
    else:

        # Charge les données d'une partie sauvegardée precedemment dans le fichier json
        with open("save.json", "r") as read_file:
            data = load(read_file)
        num_round = data[0]
        joueurs = data[1]
        plateau_jeu = data[2]
        pioche = data[3]
        plateau_bonus = data[4]
        tours_passe_consecutif = data[5]
        motsfr = plat.generer_dico(data[6])
        mots_deja_place = data[7]
        duree_partie = time.time()-data[8]
        print("\nLa partie sauvegardee a ete chargee avec succes !")

    print("\nDemarage de la partie ...\n")
    finit = [0, "premier joueur a finir"]
    
    tour_joueur(plateau_jeu, joueurs, pioche, plateau_bonus, finit, tours_passe_consecutif, num_round, motsfr,mots_deja_place)


# Permet la fin de la partie et enventuellement d'en relancer une autre
def fin_partie(info_joueurs, tours_passe_consecutif, infos_fin, num_round):

    global duree_partie

    duree_partie = round((time.time()-duree_partie))
   
    # Si la partie se finit car il n'y a plus de mot possible et que tous les joueurs on passé leur tour 3 fois de suite
    # la valeur de leur jetons restant leur est tous retranchée
    if tours_passe_consecutif >= len(info_joueurs)*3:
        for indice in info_joueurs:
            info_joueurs[indice]["score"] -= plat.valeur_mot(info_joueurs[indice]["main"])

    else:

        # Ajoute au score du premier a avoir finit la valeur des lettres restantes aux autres joueurs et leur
        # soustrait à leur propre score cette même valeur
        premier_a_finir = infos_fin[1]
        for indice in info_joueurs:
            premier_a_finir["score"] += plat.valeur_mot(info_joueurs[indice]["main"])
            info_joueurs[indice]["score"] -= plat.valeur_mot(info_joueurs[indice]["main"])
            premier_a_finir["score"] += plat.valeur_mot(premier_a_finir["main"])

    statistiques(info_joueurs, num_round)

    # permet de rejouer une partie
    rejouer = input("\nVoulez vous rejouer ? (oui / non) : ").upper()
    while rejouer != "OUI" and rejouer != "NON":
        print("Réponse invalide")
        rejouer = input("Voulez vous rejouer ? (oui / non) : ").upper()
    if rejouer == "OUI":
        debut_partie()
    else:
        print("\nMerci d'avoir joué a notre jeu et à bientôt !")

# Lance la partie
if __name__ == "__main__":
    debut_partie()
    motsfr=[]
    duree_partie=0