from main import *

def test_partie2question1():
    """
    Test de la fonction partie2question1
    192 correspond au code de l'occupation "secrétaire d'État"
    """
    partie2question1("192")

def test_partie2question2():
    """
    Test de la fonction partie2question2
    """
    partie2question2("donner des conseils sur les finances publiques")

def test_partie2question3():
    """
    Test de la fonction partie2question3
    """
    partie2question3("donner des conseils sur les finances publiques", "appliquer la gestion des conflits")

def test_partie2question4():
    """
    Test de la fonction partie2question4
    192 correspond au code de l'occupation "secrétaire d'État"
    19 correspond au code de l'occupation "chargé de mission logement/chargée de mission logement"
    """
    partie2question4("192", "19")

def test_partie2question5():
    """
    Test de la fonction partie2question5
    """
    test_skills = [
        "donner des conseils sur les finances publiques",
        "appliquer la gestion des conflits"
    ]
    partie2question5(test_skills)

def test_all():
    """
    Tester toutes les fonctions de la partie 2
    """
    test_partie2question1()
    test_partie2question2()
    test_partie2question3()
    test_partie2question4()
    test_partie2question5()

if __name__ == "__main__":
    test_all()