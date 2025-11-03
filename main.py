from data import user_consts as consts
from py2neo import Graph

# Connexion à la base de données
graph = Graph(consts.NEO4J_URI, auth=(consts.NEO4J_USERNAME, consts.NEO4J_PASSWORD))

# Menu principal
def menu():
    print("Projet BUT3APP - Système de recommandation avec Neo4j - Axel Rivière & Quentin Tripognez")
    print("1. Partie 1 - Question 1")
    print("2. Partie 2 - Question 2")
    print("9. Quitter")

    choice = input("Votre choix: ")

    if choice == '1':
        partie1question1()
    elif choice == '2':
        competence = input("Quelle compétence ?")
        partie1question2(competence)
    elif choice == '9':
        print("Au revoir !")
        return
    else:
        print("Choix invalide, veuillez réessayer.")
        menu()

# Partie 1 - Question 1 - Fiche métier
# Cette fonctionnalité permet aux utilisateurs d’afficher un métier donné avec toutes
# les compétences associées et les connaissances, ainsi que les autres appellations.
def partie1question1():
    return # TODO

# Partie 1 - Question 2 - Compétence/connaissance
# Cette fonctionnalité permet de voir une compétence ou/et connaissance donnée où
# elle est requise ou facultative et pour quels métiers
def partie1question2(skill_or_knowledge: str):
    print(f"\n{'=' * 80}")
    print(f"Recherche pour : {skill_or_knowledge}")
    print(f"{'=' * 80}\n")

    query_skill = """
    MATCH (o:Occupation)-[r:REQUIRES]->(s:Skill {name: $name})
    RETURN o.label AS occupation, o.code AS code, r.type AS requirement_type
    ORDER BY r.type, o.label
    """

    query_knowledge = """
    MATCH (o:Occupation)-[r:NEEDS_KNOWLEDGE]->(k:Knowledge {name: $name})
    RETURN o.label AS occupation, o.code AS code, r.type AS requirement_type
    ORDER BY r.type, o.label
    """

    results_skill = list(graph.run(query_skill, name=skill_or_knowledge))
    results_knowledge = list(graph.run(query_knowledge, name=skill_or_knowledge))

    all_results = results_skill + results_knowledge

    if not all_results:
        print(f"Aucun résultat trouvé pour '{skill_or_knowledge}'")
        return

    type_str = "Compétence (Skill)" if results_skill else "Connaissance (Knowledge)"
    print(f"Type : {type_str}")
    print(f"Total de métiers trouvés : {len(all_results)}\n")

    required = [r for r in all_results if r['requirement_type'] == 'required']
    optional = [r for r in all_results if r['requirement_type'] == 'optional']

    if required:
        print(f"MÉTIERS OÙ C'EST REQUIS ({len(required)}) :")
        print("-" * 80)
        for i, result in enumerate(required, 1):
            print(f" {i}. {result['occupation']} (Code: {result['code']})")
        print()
    else:
        print("MÉTIERS OÙ C'EST REQUIS : Aucun\n")

    if optional:
        print(f"MÉTIERS OÙ C'EST OPTIONNEL ({len(optional)}) :")
        print("-" * 80)
        for i, result in enumerate(optional, 1):
            print(f" {i}. {result['occupation']} (Code: {result['code']})")
        print()
    else:
        print("MÉTIERS OÙ C'EST OPTIONNEL : Aucun\n")

    print(f"{'=' * 80}\n")

def partie1question4():
    return # TODO

if __name__ == "__main__":
    menu()