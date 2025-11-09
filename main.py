from data import user_consts as consts
from py2neo import Graph

# Connexion à la base de données
graph = Graph(consts.NEO4J_URI, auth=(consts.NEO4J_USERNAME, consts.NEO4J_PASSWORD))

def menu():
    """
    Menu principal pour interagir avec les différentes fonctionnalités
    """
    print("\n" + "=" * 80)
    print("Projet BUT3APP - Système de recommandation avec Neo4j - Axel Rivière & Quentin Tripognez")
    print("=" * 80 + "\n")

    print("1. Partie 2 - Question 1 : Fiche métier")
    print("2. Partie 2 - Question 2 : Compétence/connaissance")
    print("3. Partie 2 - Question 3 : Similarité entre compétences")
    print("4. Partie 2 - Question 4 : Similarité entre métiers")
    print("5. Partie 2 - Question 5 : Recommandation de métier")
    print("6. Quitter\n")

    choice = input("Votre choix : ")

    if choice == '1':
        print("\nExemple d'utilisation : 192 (secrétaire d'État)")
        job_code = input("Code du métier : ")
        partie2question1(job_code)
        menu()
    elif choice == '2':
        print("\nExemple d'utilisation : donner des conseils sur les finances publiques")
        skill_or_knowledge = input("Nom de la compétence ou connaissance : ")
        partie2question2(skill_or_knowledge)
        menu()
    elif choice == '3':
        print("\nExemple d'utilisation : donner des conseils sur les finances publiques / appliquer la gestion des conflits")
        skill_or_knowledge1 = input("Nom de la première compétence/connaissance : ")
        skill_or_knowledge2 = input("Nom de la deuxième compétence/connaissance : ")
        partie2question3(skill_or_knowledge1, skill_or_knowledge2)
        menu()
    elif choice == '4':
        print("\nExemple d'utilisation : 192  (secrétaire d'État) / 19 (chargé de mission logement/chargée de mission logement")
        job_code1 = input("Code du premier métier : ").strip()
        job_code2 = input("Code du deuxième métier : ").strip()
        partie2question4(job_code1, job_code2)
        menu()
    elif choice == '5':
        print("\nExemple d'utilisation : donner des conseils sur les finances publiques, appliquer la gestion des conflits")
        skills_input = input("Compétences, séparées par des virgules : ")
        skills_list = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
        partie2question5(skills_list)
        menu()
    elif choice == '6':
        print("Au revoir !")
        return
    else:
        print("Choix invalide, veuillez réessayer.")
        menu()

def partie2question1(job_code: str):
    """
    Partie 2 - Question 1 - Fiche métier
    Cette fonctionnalité permet aux utilisateurs d’afficher un métier donné avec toutes
    les compétences associées et les connaissances, ainsi que les autres appellations.
    :param job_code: Code du métier à rechercher
    :return: Dictionnaire avec les résultats de la requête
    """

    print(f"\n{'=' * 80}")
    print(f"Fiche métier pour le code : {job_code}")
    print(f"{'=' * 80}\n")

    query = """
    MATCH (o:Occupation {code: $job_code})
    OPTIONAL MATCH (o)-[:REQUIRES]->(comp:Skill)
    OPTIONAL MATCH (o)-[:NEEDS_KNOWLEDGE]->(conn:Knowledge)
    RETURN o.label as metier,
           o.alt_names as appellations,
           collect(DISTINCT comp.name) as competences,
           collect(DISTINCT conn.name) as connaissances
    """
    res = graph.run(query, job_code=job_code).data()

    if res:
        result = res[0]
        print(f"Métier : {result['metier']}")
        print(f"\nAutres appellations : ")
        for i, app in enumerate(result['appellations'], 1):
            print(f" {i}. {app}")
        print(f"\nCompétences : ")
        for i, skill in enumerate(result['competences'], 1):
            print(f" {i}. {skill}")
        print(f"\nConnaissances : ")
        for i, know in enumerate(result['connaissances'], 1):
            print(f" {i}. {know}")
    else:
        print(f"Aucun métier trouvé avec le code: {job_code}")

    return res

def partie2question2(skill_or_knowledge: str):
    """
    Partie 2 - Question 2 - Compétence/connaissance
    Cette fonctionnalité permet de voir une compétence ou/et connaissance donnée où
    elle est requise ou facultative et pour quels métiers
    :param skill_or_knowledge: Nom de la compétence ou connaissance à rechercher
    :return: Dictionnaire avec les résultats de la requête
    """
    print(f"\n{'=' * 80}")
    print(f"Recherche de la compétence/connaissance : {skill_or_knowledge}")
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

    type_str = "compétence" if results_skill else "connaissance"
    print(f"Type : {type_str.title()}")
    print(f"Total de métiers trouvés : {len(all_results)}\n")

    required = [r for r in all_results if r['requirement_type'] == 'required']
    optional = [r for r in all_results if r['requirement_type'] == 'optional']

    if required:
        print(f"Métiers où la {type_str} est requise ({len(required)}) :")
        for i, result in enumerate(required, 1):
            print(f" {i}. {result['occupation']} (Code: {result['code']})")
            print()
    else:
        print(f"Métiers où la {type_str} est require : Aucun\n")

    if optional:
        print(f"Métiers où la {type_str} est optionnelle ({len(optional)}) :")
        for i, result in enumerate(optional, 1):
            print(f" {i}. {result['occupation']} (Code: {result['code']})")
    else:
        print(f"Métiers où la {type_str} est optionnelle : Aucun\n")

def partie2question3(skill_or_knowledge1: str, skill_or_knowledge2: str):
    """
    Partie 2 - Question 3 - Similarité entre compétences
    Cette fonction permet de calculer la similarité entre deux compétences données, en
    se basant sur leur co-occurrence dans les mêmes métiers. Le calcul de similarité doit
    également prendre en compte le caractère obligatoire ou facultatif de chaque compétence
    dans ces métiers.
    :param skill_or_knowledge1: Première compétence/connaissance
    :param skill_or_knowledge2: Deuxième compétence/connaissance
    :return: Dictionnaire avec les résultats de la similarité
    """

    print(f"\n{'=' * 80}")
    print(f"Similarité entre les éléments : '{skill_or_knowledge1}' et '{skill_or_knowledge2}'")
    print(f"{'=' * 80}\n")

    query = """
    MATCH (e1)
    WHERE (e1:Skill OR e1:Knowledge) AND e1.name = $skill_or_knowledge1
    MATCH (e2)
    WHERE (e2:Skill OR e2:Knowledge) AND e2.name = $skill_or_knowledge2

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
    res = graph.run(query, skill_or_knowledge1=skill_or_knowledge1, skill_or_knowledge2=skill_or_knowledge2).data()

    if res:
        result = res[0]
        intersection = result['intersection']
        union = result['union']
        similarity = result['jaccard_similarity']

        print(f"Métiers en commun (intersection) : {intersection}")
        print(f"Métiers totaux (union): {union}")
        print(f"Score de similarité: {similarity:.4f}")
    else:
        print(f"Impossible de calculer la similarité entre '{skill_or_knowledge1}' et '{skill_or_knowledge2}'")

    return res

def partie2question4(job_code1: str, job_code2: str):
    """
    Question 4 - Similarité entre métiers
    Cette fonction calcule la similarité de Jaccard entre deux métiers
    (Occupations) en se basant sur l'ensemble de leurs compétences (Skill),
    qu'elles soient obligatoires ou optionnelles.
    :param job_code1: Code du premier métier
    :param job_code2: Code du deuxième métier
    :return: Dictionnaire avec les résultats de la similarité
    """
    query = """
    // Récupérer les compétences du premier métier
    MATCH (o1:Occupation {code: $job_code1})-[r1:REQUIRES]->(s1:Skill)
    WHERE r1.type IN ['required', 'optional']
    WITH o1, collect(DISTINCT s1) AS skills1

    // Récupérer les compétences du deuxième métier
    MATCH (o2:Occupation {code: $job_code2})-[r2:REQUIRES]->(s2:Skill)
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

    res = graph.run(query, job_code1=job_code1, job_code2=job_code2).data()

    print(f"\n{'=' * 80}")
    print(f"Similarité entre les métiers {job_code1} et {job_code2}")
    print(f"{'=' * 80}\n")

    if res:
        result = res[0]
        intersection = result['intersection']
        union = result['union']
        similarity = result['jaccard_similarity']

        print(f"Compétences en commun (intersection) : {intersection}")
        print(f"Compétences totales distinctes (union) : {union}")
        print(f"Score de similarité (Jaccard) : {similarity:.5f}")
    else:
        print(f"Impossible de calculer la similarité entre '{job_code1}' et '{job_code2}'")

    return res


def partie2question5(skills: list):
    """
    Question 5. Recommandation métier :
    Cette fonctionnalité permet de retourner une liste des métiers à recommander
    au utilisateur selon ses compétences données.
    :param skills: Liste des compétences de l'utilisateur
    :return: Dictionnaire avec les résultats de la recommandation
    """
    print(f"\n{'=' * 80}")
    print(f"Recommandation de métiers pour les compétences :")
    for skill in skills:
        print(f" - {skill}")
    print(f"{'=' * 80}\n")

    query = """
    // Récupérer tous les métiers avec leurs compétences
    MATCH (o:Occupation)-[r:REQUIRES]->(s:Skill)
    WHERE s.name IN $skills
    WITH o, count(DISTINCT s) AS matching_skills

    // Compter le nombre total de compétences pour chaque métier
    MATCH (o)-[r:REQUIRES]->(all_skills:Skill)
    WITH o, matching_skills, count(DISTINCT all_skills) AS total_skills
    WHERE matching_skills > 0

    // Calculer le score de correspondance
    WITH o, matching_skills, total_skills,
         toFloat(matching_skills) / toFloat(total_skills) AS score

    RETURN o.code AS code, 
           o.label AS metier,
           matching_skills,
           total_skills,
           score
    ORDER BY score DESC
    LIMIT 5
    """

    res = graph.run(query, skills=skills).data()

    translation_dict = {
        "matching_skills": "Compétences correspondantes",
        "total_skills": "Compétences totales",
        "score": "Score de correspondance"
    }

    if res:
        for i, result in enumerate(res, 1):
            print(f" {i}. {result['metier']} (Code: {result['code']})")
            for key, value in translation_dict.items():
                print(f" - {value} : {result[key]}")
            if i < len(res):
                print()
    else:
        print("Aucun métier trouvé correspondant à ces compétences.")

    return res

if __name__ == "__main__":
    menu()
