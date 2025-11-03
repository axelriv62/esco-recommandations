def menu():
    print("Projet BUT3APP - Système de recommandation avec Neo4j - Axel Rivière & Quentin Tripognez")
    print("1. Partie 1 - Question 1")
    print("2. Partie 2 - Question 2")
    print("9. Quitter")

    choice = input("Votre choix: ")

    if choice == '1':
        partie1question1()
    elif choice == '2':
        partie1question2()
    elif choice == '9':
        print("Au revoir !")
    else:
        print("Choix invalide, veuillez réessayer.")
        menu()

def partie1question1():
    return # TODO

def partie1question2():
    return # TODO