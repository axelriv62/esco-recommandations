from data import user_consts as consts
from py2neo import Graph

# Connexion à la base de données
graph = Graph(consts.NEO4J_URI, auth=(consts.NEO4J_USERNAME, consts.NEO4J_PASSWORD))

# Menu principal
def menu():
    print("\n1. Partie 1 - Question 1")
    print("2. Partie 1 - Question 2")
    print("3. Partie 1 - Question 3")
    print("9. Quitter\n")

    choice = input("Votre choix: ")

    if choice == '1':
        code_metier = input("\nVeillez entrer le code du métier souhaité: ")
        partie1question1(code_metier)
        menu()
    elif choice == '2':
        partie1question2()
        menu()
    elif choice == '3':
        element1 = input("\nVeuillez entrer le nom de la première compétence/connaissance: ")
        element2 = input("Veuillez entrer le nom de la deuxième compétence/connaissance: ")
        partie1question3(element1, element2)
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

# Partie 1 - Question 3 - Similarité entre compétences
# Cette fonction permet de calculer la similarité entre deux compétences données, en
# se basant sur leur co-occurrence dans les mêmes métiers. Le calcul de similarité doit
# également prendre en compte le caractère obligatoire ou facultatif de chaque compétence
# dans ces métiers.
def partie1question3(element1: str, element2: str):
    query = """
    MATCH (e1)
    WHERE (e1:Skill OR e1:Knowledge) AND e1.name = $element1
    MATCH (e2)
    WHERE (e2:Skill OR e2:Knowledge) AND e2.name = $element2

    // Métiers ayant e1
    OPTIONAL MATCH (e1)<-[r1]-(o1:Occupation)
    WHERE type(r1) IN ['REQUIRES', 'NEEDS_KNOWLEDGE']

    // Métiers ayant e2
    WITH e1, e2, collect(DISTINCT o1) as metiers_e1
    OPTIONAL MATCH (e2)<-[r2]-(o2:Occupation)
    WHERE type(r2) IN ['REQUIRES', 'NEEDS_KNOWLEDGE']

    // Métiers ayant les deux (intersection)
    WITH e1, e2, metiers_e1, collect(DISTINCT o2) as metiers_e2
    OPTIONAL MATCH (e1)<-[r1_inter]-(o_inter:Occupation)-[r2_inter]->(e2)
    WHERE type(r1_inter) IN ['REQUIRES', 'NEEDS_KNOWLEDGE']
      AND type(r2_inter) IN ['REQUIRES', 'NEEDS_KNOWLEDGE']

    WITH metiers_e1, metiers_e2, collect(DISTINCT o_inter) as metiers_intersection

    // Filtrer les valeurs null avant de calculer la taille
    WITH [x IN metiers_e1 WHERE x IS NOT NULL] as m1,
         [x IN metiers_e2 WHERE x IS NOT NULL] as m2,
         [x IN metiers_intersection WHERE x IS NOT NULL] as m_inter

    WITH size(m_inter) as intersection,
         size(m1) + size(m2) - size(m_inter) as union

    RETURN intersection, union,
           CASE WHEN union > 0
                THEN toFloat(intersection) / toFloat(union)
                ELSE 0.0
           END as jaccard_similarity
    """
    res = graph.run(query, element1=element1, element2=element2).data()

    if res:
        result = res[0]
        intersection = result['intersection']
        union = result['union']
        similarity = result['jaccard_similarity']

        print(f"Intersection (métiers en commun): {intersection}")
        print(f"Union (métiers totaux): {union}")
        print(f"Score de similarité: {similarity:.4f}")
    else:
        print(f"Impossible de calculer la similarité entre '{element1}' et '{element2}'")

    return res

if __name__ == "__main__":
    print("\nProjet BUT3APP - Système de recommandation avec Neo4j - Axel Rivière & Quentin Tripognez")
    menu()