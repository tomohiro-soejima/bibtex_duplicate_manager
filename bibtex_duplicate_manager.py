import bibtexparser
from bibtexparser.bparser import BibTexParser
import re
from collections import defaultdict
import string
import numpy as np

def load_bibtex_files(filenames):
    entries = []
    for filename in filenames:
        with open(filename) as bibtex_file:
            parser = BibTexParser(common_strings=True)
            bib_database = bibtexparser.load(bibtex_file, parser=parser)
            entries.extend(bib_database.entries)
    return entries

def is_subsequence(words_a, words_b):
    """Check if words_a is a subsequence of words_b."""
    iter_b = iter(words_b)
    return all(word in iter_b for word in words_a)

def remove_double_braces(s):
    """Bibtex files sometimes contain double braces around words i.e. {{WORD}}
    This complicates comparison between bibtex entries, so we remove them using this function"""
    return re.sub(r'\{\{([^}]*)\}\}', r'\1', s)

def find_potential_duplicates(entries, num_tol = 7):
    """Find potential duplicates by comparing if two titles share a subsequence of length > num_tol"""
    potential_duplicates = defaultdict(list)

    for i in range(len(entries)):
        title_i_str = entries[i].get('title', entries[i].get("Title", '') )
        title_i_without_brace = remove_double_braces(title_i_str)
        title_i = title_i_without_brace.translate(str.maketrans('', '', string.punctuation)).lower().split()
        if title_i_str in potential_duplicates.keys():
            continue
        potential_duplicates[title_i_str].append(entries[i])
        for j in range(i+1, len(entries)):
            title_j_str = entries[j].get('title', entries[j].get("Title", '') )
            title_j_without_brace = remove_double_braces(title_j_str)
            title_j = title_j_without_brace.translate(str.maketrans('', '', string.punctuation)).lower().split()
            # print("embed")
            # import IPython; IPython.embed()
            if title_j_str.lower().startswith("Unconventional") and title_i_str.lower().startswith("unconventional superconductivity"):
                import IPython; IPython.embed()

            # Check if titles have a shared subsequence of num_tol words in the same order
            for k in range(len(title_i) - num_tol + 1): # -(num_tol + 1) to ensure we take subsequences of at least 7 words
                if is_subsequence(title_i[k:k+num_tol], title_j):
                    potential_duplicates[title_i_str].append(entries[j])
                    break

    # Only keep lists of entries that have more than one entry (potential duplicates)
    duplicates = {title: entries for title, entries in potential_duplicates.items() if len(entries) > 1}
    return duplicates

def filter_duplicates(duplicates, filenames):
    """Given a potential set of duplicates, check whether more than one citekeys show up in the file list. Otherwise, no need to replace citekeys"""
    duplicates_filtered = {}
    for title, entries in duplicates.items():
        citekeys = [entry["ID"] for entry in entries]
        check = check_citekeys_occurence(filenames, citekeys)
        if check:
            duplicates_filtered[title] = entries.copy()
            for entry in entries:
                entry["occurences"] = find_citekey_in_files(filenames, entry["ID"], False)[1]

    return duplicates_filtered

def replace_keys_in_tex_files(file_list, old_citekeys, new_citekey):
    for old_citekey in old_citekeys:
        # Regular expression to find old_citekey within \cite{}
        # Takes care of the fact \cite{} might contain multiple citekeys
        pattern_str = r'(\\cite\{[^}]*\b)' + re.escape(old_citekey) + r'(\b[^}]*\})'
        pattern = re.compile(pattern_str)

        for filename in file_list:
            with open(filename, 'r') as file:
                content = file.read()

            # Replace old_citekey with new_citekey
            new_content = pattern.sub(r'\1' + new_citekey + r'\2', content)

            with open(filename, 'w') as file:
                file.write(new_content)

            print(f"All occurrences of '{old_citekey}' in {filename} have been replaced with '{new_citekey}'.")

def check_citekeys_occurence(file_list, citekeys):
    citekeys_unique = set(citekeys)
    found_list = []
    for key in citekeys_unique:
        found_list.append(find_citekey_in_files(file_list, key)[0])

    return np.sum(found_list) > 1

def find_citekey_in_files(file_list, citekey, verbose=False):
    # Regular expression to match \cite{citekey1, citekey2, ...}
    pattern_str = r'\\cite\{[^}]*\b' + re.escape(citekey) + r'\b[^}]*\}'
    pattern = re.compile(pattern_str)

    found = False
    num_occured = 0

    for filename in file_list:
        with open(filename, 'r') as file:
            content = file.read()
            matches = pattern.findall(content)
            if matches:
                num_occured = len(matches)
                found = True
                if verbose:
                    print(f"The citekey '{citekey}' was found in {filename}:")
                    for match in matches:
                        print(f"  {match}")
                    print(f"Occurences: {num_occured}")

    return found, num_occured

if __name__ == "__main__":
    # Let's make it interactive!
    print("Welcome to the BibTeX duplicate cleaner!")
    bib_files = input("Enter the paths to the .bib files, separated by commas: ").split(',')
    tex_files = input("Enter the paths to the .tex files, separated by commas: ").split(',')

    entries = load_bibtex_files(bib_files)
    nonzero_entries = [entry for entry in entries if find_citekey_in_files(tex_files, entry["ID"])[0]]
    duplicates = find_potential_duplicates(nonzero_entries, 5)
    duplicates_filtered = filter_duplicates(duplicates, tex_files)

    # import IPython; IPython.embed()

    new_duplicates = {}

    for title, duplicate_entries in duplicates_filtered.items():
        print("new entry")
        items = [(title, duplicate_entries)]
        num_tol = 5
        while len(items) > 0 :
            title2, duplicate_entries2 = items.pop(0)
            if len(duplicate_entries2) < 6:
                print(f"\nPotential duplicates for '{title2}':")
                for i, entry in enumerate(duplicate_entries2):
                    print(f"{i+1}: {entry.get('title', 'No title')} (key: {entry.get('ID', 'No ID')}) (occur: {entry.get('occurences', 0)})")
                confirm = input("Treat these as duplicates? (yes/no) ")

            if len(duplicate_entries2) > 5 or confirm.lower() != 'yes':
                # when the list of duplicates mistakenly identifies non-duplicate items,
                # try comparison again with larger num_tol
                current_length = len(duplicate_entries2)
                while True:
                    num_tol += 1
                    duplicates2 = find_potential_duplicates(duplicate_entries2, num_tol=num_tol)
                    duplicates_filtered2 = filter_duplicates(duplicates2, tex_files)
                    print([(item[0], len(item[1])) for item in duplicates2.items()])
                    print([(item[0], len(item[1])) for item in duplicates_filtered2.items()])
                    # prepend the newly found entries to duplicates
                    if len(duplicates_filtered2) == 0 or current_length > len(next(iter(duplicates_filtered2.values()))):
                        break
                items = [(title, entries) for (title, entries) in duplicates_filtered2.items()] + items
                continue

            num_tol = 5
            while True:
                keep = int(input("Enter the number of the key to keep: ")) - 1
                if 0 <= keep < len(duplicate_entries):
                    break
                print("Invalid number!")

            replace_keys_in_tex_files(tex_files, [entry.get('ID') for i, entry in enumerate(duplicate_entries2) if i != keep], duplicate_entries2[keep].get('ID'))

    print("Done cleaning duplicates!")
