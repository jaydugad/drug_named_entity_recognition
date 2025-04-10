'''
MIT License

Copyright (c) 2023 Fast Data Science Ltd (https://fastdatascience.com)

Maintainer: Thomas Wood

Tutorial at https://fastdatascience.com/drug-named-entity-recognition-python-library/

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

import bz2
import pickle
from pathlib import Path

def load_drug_dictionary(dict_path):
    with bz2.open(dict_path, "rb") as f:
        return pickle.load(f)

def save_updated_dictionary(drugs_dict, output_path):
    with bz2.open(output_path, "wb") as f:
        pickle.dump(drugs_dict, f)

def load_smiles_data(smiles_path):
    cid_to_smiles = {}
    with open(smiles_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i % 500000 == 0:
                print(f"[INFO] Processed {i} SMILES lines...")
            parts = line.strip().split('\t')
            if len(parts) == 2:
                cid, smiles = parts
                cid_to_smiles[cid.strip()] = smiles.strip()
    return cid_to_smiles

def load_cid_to_mesh_mapping(mesh_map_path):
    cid_to_mesh = {}
    with open(mesh_map_path, 'r', encoding='utf-8') as f:
        for line in f:
            cols = line.strip().split('\t')
            if len(cols) >= 2:
                cid, mesh_id = cols[:2]
                cid_to_mesh[cid.strip()] = mesh_id.strip()
    return cid_to_mesh

def patch_smiles_by_mesh(drugs_dict, cid_to_smiles, cid_to_mesh):
    mesh_to_smiles = {}
    for cid, mesh_id in cid_to_mesh.items():
        if cid in cid_to_smiles:
            mesh_to_smiles[mesh_id] = cid_to_smiles[cid]

    matched = 0
    canonical_to_data = drugs_dict["drug_canonical_to_data"]
    for canonical, entry in canonical_to_data.items():
        mesh_id = entry.get("mesh_id")
        if mesh_id and mesh_id in mesh_to_smiles and "smiles" not in entry:
            entry["smiles"] = mesh_to_smiles[mesh_id]
            matched += 1

    print(f"Added SMILES to {matched} drugs using MeSH IDs.")
    return drugs_dict

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent / "src" / "drug_named_entity_recognition"
    dict_path = base_dir / "drug_ner_dictionary.pkl.bz2"
    smiles_path = base_dir / "pubchem_data" / "CID-SMILES"
    cid_mesh_path = base_dir / "pubchem_data" / "CID-MeSH.txt"
    output_path = dict_path  # or a separate output file

    print(f"[INFO] Loading data...")
    drugs_dict = load_drug_dictionary(dict_path)
    cid_to_smiles = load_smiles_data(smiles_path)
    cid_to_mesh = load_cid_to_mesh_mapping(cid_mesh_path)
    updated_dict = patch_smiles_by_mesh(drugs_dict, cid_to_smiles, cid_to_mesh)
    save_updated_dictionary(updated_dict, output_path)
