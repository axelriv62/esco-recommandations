# Projet BDD - Système de recommandation avec Neo4j 
Par Axel Rivière et Quentin Tripognez (BUT3 APP)

## Lancer le projet
```commandline
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Requêtes Cypher de la Section 3

### Question 1. Fiche métier : Cette question se base sur la question 1 de la Section 2.
> Donner la requête qui affiche les compétences d’un métier en Cypher.

```cypher
MATCH (o:Occupation {code: "192"})-[:REQUIRES]->(s:Skill)
RETURN o.label as metier, s.name as competence
```

> Donner la requête qui affiche les compétences et les connaissances d’un métier en Cypher avec la fonction ’collect’.

```cypher
MATCH (o:Occupation {code: "192"})
OPTIONAL MATCH (o)-[:REQUIRES]->(s:Skill)
OPTIONAL MATCH (o)-[:NEEDS_KNOWLEDGE]->(k:Knowledge)
RETURN o.label as metier,
       o.alt_names as appellations,
       collect(DISTINCT s.name) as competences,
       collect(DISTINCT k.name) as connaissances
```

### Question 2. Fiche compétence/connaissance : Cette question se base sur la question 2 de la Section 2.
> Donner la requête qui affiche les métiers qui requièrent une compétence spécifique en Cypher.

```cypher
MATCH (o:Occupation)-[r:REQUIRES]->(s:Skill {name: "Maîtriser Excel"})
RETURN
  o.label AS metier,
  o.code  AS code,
  r.type  AS type_exigence
ORDER BY r.type, o.label;
```
 
> Donner la requête qui affiche les métiers qui requièrent une connaissance spécifique en Cypher.

```cypher
MATCH (o:Occupation)-[r:NEEDS_KNOWLEDGE]->(k:Knowledge {name: "Droit du travail"})
RETURN
  o.label AS metier,
  o.code  AS code,
  r.type  AS type_exigence
ORDER BY r.type, o.label;
```

### Question 3. Similarité entre compétences : Cette question se base sur la question 3 de la Section 2.
> Donner la requête qui calcule le score de similarité, avec le coefficient de Jaccard, entre 2 compétences spécifiques. 

```cypher
MATCH (e1)
WHERE (e1:Skill OR e1:Knowledge) AND e1.name = "donner des conseils sur les finances publiques"
MATCH (e2)
WHERE (e2:Skill OR e2:Knowledge) AND e2.name = "appliquer la gestion des conflits"

OPTIONAL MATCH (e1)<-[r1]-(o1:Occupation)
WHERE type(r1) IN ['REQUIRES', 'NEEDS_KNOWLEDGE']

WITH e1, e2, collect(DISTINCT o1) as metiers_e1
OPTIONAL MATCH (e2)<-[r2]-(o2:Occupation)
WHERE type(r2) IN ['REQUIRES', 'NEEDS_KNOWLEDGE']

WITH e1, e2, metiers_e1, collect(DISTINCT o2) as metiers_e2
OPTIONAL MATCH (e1)<-[r1_inter]-(o_inter:Occupation)-[r2_inter]->(e2)
WHERE type(r1_inter) IN ['REQUIRES', 'NEEDS_KNOWLEDGE']
  AND type(r2_inter) IN ['REQUIRES', 'NEEDS_KNOWLEDGE']

WITH metiers_e1, metiers_e2, collect(DISTINCT o_inter) as metiers_intersection

WITH [x IN metiers_e1 WHERE x IS NOT NULL] as m1,
     [x IN metiers_e2 WHERE x IS NOT NULL] as m2,
     [x IN metiers_intersection WHERE x IS NOT NULL] as m_inter

WITH size(m_inter) as intersection,
     size(m1) + size(m2) - size(m_inter) as union

RETURN intersection, 
       union,
       CASE WHEN union > 0
            THEN toFloat(intersection) / toFloat(union)
            ELSE 0.0
       END as jaccard_similarity
```

### Question 4. Similarité entre métiers : Cette question se base sur la question 4 de la Section 2.
> Donner la requête qui calcule le score de similarité, avec le coefficient de Jaccard, entre 2 métiers spécifiques. 

```cypher
MATCH (o1:Occupation {code: "3115"})-[r1:REQUIRES]->(s1:Skill)
WHERE r1.type IN ['required', 'optional']
WITH o1, collect(DISTINCT s1) AS skills1

MATCH (o2:Occupation {code: "1219"})-[r2:REQUIRES]->(s2:Skill)
WHERE r2.type IN ['required', 'optional']
WITH skills1, collect(DISTINCT s2) AS skills2

WITH
  [x IN skills1 WHERE x IS NOT NULL] AS m1,
  [x IN skills2 WHERE x IS NOT NULL] AS m2,
  [x IN skills1 WHERE x IN skills2]  AS inter

WITH
  m1,
  m2,
  inter,
  size(inter)                         AS intersection,
  size(m1) + size(m2) - size(inter)   AS union

RETURN
  intersection,
  union,
  CASE
    WHEN union > 0
    THEN toFloat(intersection) / toFloat(union)
    ELSE 0.0
  END AS jaccard_similarity;
```

### Question 5. Recommandation métier : Cette question se base sur la question 5 de la Section 2.
> Donner la requête qui trouve certains métiers qui correspondent mieux aux compétences d’un utilisateur et qui les trie à la fin par score.

```cypher
MATCH (o:Occupation)-[r:REQUIRES]->(s:Skill)
WHERE s.name IN ["donner des conseils sur les finances publiques", "appliquer la gestion des conflits"]
WITH o, count(DISTINCT s) AS matching_skills

MATCH (o)-[:REQUIRES]->(all_skills:Skill)
WITH o, matching_skills, count(DISTINCT all_skills) AS total_skills
WHERE matching_skills > 0

WITH o, matching_skills, total_skills,
     toFloat(matching_skills) / toFloat(total_skills) AS score

RETURN o.code AS code,
       o.label AS metier,
       matching_skills,
       total_skills,
       score
ORDER BY score DESC
```