from data import user_consts as consts
from py2neo import Graph

# Connexion à la base de données
graph = Graph(consts.NEO4J_URI, auth=(consts.NEO4J_USERNAME, consts.NEO4J_PASSWORD))

# Menu principal
def menu():
    print("\n1. Partie 1 - Question 1")
    print("2. Partie 2 - Question 2")
    print("9. Quitter\n")

    choice = input("Votre choix: ")

    if choice == '1':
        code_metier = input("\nVeillez entrer le code du métier souhaité: ")
        partie1question1(code_metier)
        menu()
    elif choice == '2':
        partie1question2()
        menu()
    elif choice == '9':
        print("Au revoir !")
        return
    else:
        print("Choix invalide, veuillez réessayer.")
        menu()

# Partie 1 - Question 1 - Fiche métier
# Cette fonctionnalité permet aux utilisateurs d’afficher un métier donné avec toutes
# les compétences associées et les connaissances, ainsi que les autres appellations.
def partie1question1(code_metier: str):
    query = """
    MATCH (o:Occupation {code: $code_metier})
    OPTIONAL MATCH (o)-[:REQUIRES]->(comp:Skill)
    OPTIONAL MATCH (o)-[:NEEDS_KNOWLEDGE]->(conn:Knowledge)
    RETURN o.label as metier,
           o.alt_names as appellations,
           collect(DISTINCT comp.name) as competences,
           collect(DISTINCT conn.name) as connaissances
    """
    res = graph.run(query, code_metier=code_metier).data()

    if res:
        result = res[0]
        print(f"\nMétier: {result['metier']}")
        print(f"Compétences: {', '.join(result['competences']) if result['competences'] else 'Aucune'}")
        print(f"Connaissances: {', '.join(result['connaissances']) if result['connaissances'] else 'Aucune'}")
        print(f"Appellations: {', '.join(result['appellations']) if result['appellations'] else 'Aucune'}")
    else:
        print(f"Aucun métier trouvé avec le code: {code_metier}")

    return res

# Partie 1 - Question 2 - Compétence/connaissance
# Cette fonctionnalité permet de voir une compétence ou/et connaissance donnée où
# elle est requise ou facultative et pour quels métiers
def partie1question2():
    return # TODO

if __name__ == "__main__":
    print("\nProjet BUT3APP - Système de recommandation avec Neo4j - Axel Rivière & Quentin Tripognez")
    menu()