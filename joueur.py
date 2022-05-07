from random import *
import copy
from json import *
import time
import plateau as plat
import joueur as jo

# Affiche la main du joueur dans la console
def afficher_main(liste_main):
    if len(liste_main) > 0:
        return " | ".join(liste_main)
    else:
        print("Vous n'avez plus de jetons")


# Cette fonction pioche x jetons dans le sac et renvoie le tirage
def piocher(x, sac):
    tirage = []
    for i in range(x):
        choix = choice(sac)
        sac.remove(choix)
        tirage.append(choix)

    return tirage


# Cette focntion complète la main du joueur
def completer_main(liste_main, sac):
    while len(liste_main) < 7 and len(sac) > 0:
        liste_main.extend(piocher(1, sac))


# Cette fonction change les lettres d'un joueur ou renvoie True si le joueur na pas les lettres qu'il veut changer
def echanger(jetons, liste_main, sac):
    jetons = list(jetons)

    # Verifie que le joueur a bien les lettres qu'il souhaite changer
    for lettre in jetons:
        if lettre not in liste_main or liste_main.count(lettre) < jetons.count(lettre):
            return True

    # Remet les lettres que le joueur veut changer dans le sac
    for j in jetons:
        liste_main.remove(j)
        sac.append(j)

    # Complète la main du joueur avec des lettres du sac
    completer_main(liste_main, sac)