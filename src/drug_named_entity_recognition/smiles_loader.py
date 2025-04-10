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

import gzip
import bz2
import pickle
from pathlib import Path

# Load drug dictionary
def load_drug_dictionary(dict_path):
    with bz2.open(dict_path, "rb") as f:
        return pickle.load(f)

# Save updated dictionary
def save_updated_dictionary(drugs_dict, output_path):
    with bz2.open(output_path, "wb") as f:
        pickle.dump(drugs_dict, f)

# Load SMILES from plain text (not gzipped)
def load_smiles_data(smiles_path):
    name_to_smiles = {}
    with open(smiles_path, 'r', encoding='utf-8') as f:
        print("[INFO] SMILES file opened, starting to parse lines...")

        for i, line in enumerate(f):
            if i % 500000 == 0:
                print(f"[INFO] Processed {i} SMILES lines...")

            parts = line.strip().split('\t')
            if len(parts) == 2:
                cid, smiles = parts
                name_to_smiles[cid] = smiles

    print(f"[INFO] Finished parsing SMILES file. Total lines: {i+1}")
    return name_to_smiles

# Attempt to match drug names or synonyms to SMILES lines
def match_smiles_to_drugs(drugs_dict, smiles_lines):
    canonical_to_data = drugs_dict["drug_canonical_to_data"]
    variant_to_canonical = drugs_dict["drug_variant_to_canonical"]

    matched = 0
    for variant in variant_to_canonical:
        for smiles_name in smiles_lines:
            if variant.lower() == smiles_name.lower():
                canonicals = variant_to_canonical[variant]
                for canonical in canonicals:
                    canonical_data = canonical_to_data.get(canonical)
                    if canonical_data is not None and "smiles" not in canonical_data:
                        canonical_data["smiles"] = smiles_lines[smiles_name]
                        matched += 1
    print(f"[✓] Added SMILES to {matched} drugs.")
    return drugs_dict

# Entry point
if __name__ == "__main__":
    base_path = Path(__file__).parent.resolve()
    dict_path = base_path / "drug_ner_dictionary.pkl.bz2"
    smiles_path = base_path / "pubchem_data" / "CID-SMILES"
    output_path = base_path / "drug_ner_dictionary_with_smiles.pkl.bz2"

    print(f"[INFO] Looking for SMILES file at: {smiles_path}")

    drugs_dict = load_drug_dictionary(dict_path)
    smiles_lines = load_smiles_data(smiles_path)
    updated_dict = match_smiles_to_drugs(drugs_dict, smiles_lines)
    save_updated_dictionary(updated_dict, output_path)
