from data import user_consts as consts
from py2neo import Graph

# Connexion à la base de données
graph = Graph(consts.NEO4J_URI, auth=(consts.NEO4J_USERNAME, consts.NEO4J_PASSWORD))

# Menu principal
def menu():
    print("Projet BUT3APP - Système de recommandation avec Neo4j - Axel Rivière & Quentin Tripognez")
    print("1. Partie 1 - Question 1")
    print("2. Partie 2 - Question 2")
    print("4. Partie 1 - Question 4 : Similarité entre métiers")
    print("9. Quitter")

    choice = input("Votre choix: ")

    if choice == '1':
        partie1question1()
    elif choice == '2':
        competence = input("Quelle compétence ?")
        partie1question2(competence)
    elif choice == '4':
        code1 = input("Code du premier métier (ex: 3115) : ").strip()
        code2 = input("Code du deuxième métier (ex: 1219) : ").strip()
        partie1question4(code1, code2)
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

def partie1question4(code1: str, code2: str):
    """
    Question 4 - Similarité entre métiers
    Cette fonction calcule la similarité de Jaccard entre deux métiers
    (Occupations) en se basant sur l'ensemble de leurs compétences (Skill),
    qu'elles soient obligatoires ou optionnelles.
    """

    query = """
    // Récupérer les compétences du premier métier
    MATCH (o1:Occupation {code: $code1})-[r1:REQUIRES]->(s1:Skill)
    WHERE r1.type IN ['required', 'optional']
    WITH o1, collect(DISTINCT s1) AS skills1

    // Récupérer les compétences du deuxième métier
    MATCH (o2:Occupation {code: $code2})-[r2:REQUIRES]->(s2:Skill)
    WHERE r2.type IN ['required', 'optional']
    WITH skills1, collect(DISTINCT s2) AS skills2

    // Calcul de l'intersection et de l'union
    WITH
        [x IN skills1 WHERE x IS NOT NULL] AS m1,
        [x IN skills2 WHERE x IS NOT NULL] AS m2,
        [x IN skills1 WHERE x IN skills2] AS inter

    WITH
        m1,
        m2,
        inter,
        size(inter) AS intersection,
        size(m1) + size(m2) - size(inter) AS union

    RETURN
        intersection,
        union,
        CASE
            WHEN union > 0 THEN toFloat(intersection) / toFloat(union)
            ELSE 0.0
        END AS jaccard_similarity
    """

    res = graph.run(query, code1=code1, code2=code2).data()

    print(f"\n{'=' * 80}")
    print(f"Similarité entre les métiers {code1} et {code2}")
    print(f"{'=' * 80}\n")

    if res:
        result = res[0]
        intersection = result['intersection']
        union = result['union']
        similarity = result['jaccard_similarity']

        print(f"Intersection (compétences en commun) : {intersection}")
        print(f"Union (compétences totales distinctes) : {union}")
        print(f"Score de similarité (Jaccard)        : {similarity:.5f}")
    else:
        print(f"Impossible de calculer la similarité entre '{code1}' et '{code2}'")

    return res


if __name__ == "__main__":
    menu()