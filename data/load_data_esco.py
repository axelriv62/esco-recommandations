from py2neo import Graph, Node, Relationship
import pandas as pd
import tqdm
import re

_SPLIT_RE = re.compile(r"\s*,\s*")

from data import user_consts as consts

graph = Graph(consts.NEO4J_URI, auth=(consts.NEO4J_USERNAME, consts.NEO4J_PASSWORD))
graph.delete_all()



def _split_list_field(s: str) -> list[str]:
    if s is None:
        return []
    if isinstance(s, float) and pd.isna(s):
        return []
    s = str(s).strip()
    if s == "" or s.lower() == "none" or s.lower() == "nan":
        return []
    parts = [p.strip() for p in _SPLIT_RE.split(s) if p.strip() != ""]
    # remove duplicates while preserving order
    seen = set()
    out = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out

def create_constraints(graph):
    graph.run("CREATE CONSTRAINT IF NOT EXISTS FOR (o:Occupation) REQUIRE o.code IS UNIQUE")
    graph.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE")
    graph.run("CREATE CONSTRAINT IF NOT EXISTS FOR (k:Knowledge) REQUIRE k.name IS UNIQUE")

def load_csv_to_neo4j(graph, csv_path: str, commit_batch: int = 200, limit: int | None = None):
    """
    Charge le CSV CSV_PATH dans Neo4j.
    Attendu : colonnes 'code', 'occupation', 'alt', 'requeredSkills', 'optionalSkills', 'requeredKnowledges', 'optionalKnowledge'
    """
    create_constraints(graph)
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False, na_values=[''])
    # Normalisation des noms de colonnes si nécessaire
    # mapping minimal si colonnes ont espaces etc.
    expected_cols = ['code','occupation','alt','requeredSkills','optionalSkills','requeredKnowledges','optionalKnowledge']
    for c in expected_cols:
        if c not in df.columns:
            raise ValueError(f"Colonne attendue manquante dans CSV: {c}")

    tx = graph.begin()
    count = 0
    N = len(df)
    for idx, row in tqdm.tqdm(df.iterrows(), total=N if limit is None else min(N, limit), desc=f"Importing data from {csv_path} ", colour='red'):
        code = row['code'].strip() if row['code'] else f"row_{idx}"
        label = row['occupation'].strip() if row['occupation'] else f"Occupation {code}"
        alt_names = _split_list_field(row.get('alt', ""))
        req_skills = _split_list_field(row.get('requeredSkills', ""))
        opt_skills = _split_list_field(row.get('optionalSkills', ""))
        req_knowledge = _split_list_field(row.get('requeredKnowledges', ""))
        opt_knowledge = _split_list_field(row.get('optionalKnowledge', ""))

        # Create / merge occupation
        occ_node = Node("Occupation", code=code, label=label, alt_names=alt_names)
        tx.merge(occ_node, "Occupation", "code")

        # Skills required
        for s in req_skills:
            sk_node = Node("Skill", name=s)
            tx.merge(sk_node, "Skill", "name")
            rel = Relationship(occ_node, "REQUIRES", sk_node, type="required")
            tx.merge(rel, "Occupation", "code")  # merge by start node key

        # Skills optional
        for s in opt_skills:
            sk_node = Node("Skill", name=s)
            tx.merge(sk_node, "Skill", "name")
            rel = Relationship(occ_node, "REQUIRES", sk_node, type="optional")
            tx.merge(rel, "Occupation", "code")

        # Knowledge required
        for k in req_knowledge:
            kn_node = Node("Knowledge", name=k)
            tx.merge(kn_node, "Knowledge", "name")
            rel = Relationship(occ_node, "NEEDS_KNOWLEDGE", kn_node, type="required")
            tx.merge(rel, "Occupation", "code")

        # Knowledge optional
        for k in opt_knowledge:
            kn_node = Node("Knowledge", name=k)
            tx.merge(kn_node, "Knowledge", "name")
            rel = Relationship(occ_node, "NEEDS_KNOWLEDGE", kn_node, type="optional")
            tx.merge(rel, "Occupation", "code")

        count += 1
        if count % commit_batch == 0:
            graph.commit(tx)
            tx = graph.begin()

        if limit and count >= limit:
            break

    graph.commit(tx)
    print(f"Chargé {count} lignes depuis {csv_path}.")

load_csv_to_neo4j(graph,"./full_occupation_fr.csv", limit=301)  # Il y a une limite car ça prend du temps à charger et il n'est pas nécessaire d'avoir l'intégralité des données pour faire quelques tests.