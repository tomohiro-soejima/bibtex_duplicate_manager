# bibtex_duplicate_manager

Checks multiple `.bib` files for near-duplicate entries, and updates citekeys in `\cite{}` statements of specified `.tex` file(s).
Useful when combining multiple `.bib` files and `.tex` files into a larger document (e.g. thesis writing).

# Usage

```bash
> python bibtex_duplicate_manager.py
> Welcome to the BibTeX duplicate cleaner!
> Enter the paths to the .bib files, separated by commas: chap2/references.bib,chap3/references.bib,chap4/references.bib # comma separated list of reference .bib files
> Enter the paths to the .tex files, separated by commas: chap2/chap2.tex,chap2/supp.tex,chap3/chap3.tex,chap3/supp.tex,chap4/chap4.tex,chap4/supp.tex # comma separated list of reference .tex files
>
Potential duplicates for '{Strongly Correlated Chern Insulators in Magic-Angle Twisted Bilayer Graphene}':
# title, citekey, and the number of times the citekey occurs accross `.tex` files.
1: {Strongly Correlated Chern Insulators in Magic-Angle Twisted Bilayer Graphene} (key: YazdaniChern) (occur: 1)
2: {Strongly Correlated Chern Insulators in Magic-Angle Twisted Bilayer Graphene} (key: Yazdani2022) (occur: 1)
3: {Chern Insulators and Topological Flat-bands in Magic-angle Twisted Bilayer Graphene} (key: AndreiChern) (occur: 0)
4: Chern Insulators, van {{Hove}} Singularities and Topological Flat Bands in Magic-Angle Twisted Bilayer Graphene (key: wu2021Chern) (occur: 2)
Treat these as duplicates? (yes/no) no # answer if the listed entries correspond to the same file

Potential duplicates for '{Strongly Correlated Chern Insulators in Magic-Angle Twisted Bilayer Graphene}':
# title, citekey, and the number of times the citekey occurs accross `.tex` files.
1: {Strongly Correlated Chern Insulators in Magic-Angle Twisted Bilayer Graphene} (key: YazdaniChern) (occur: 1)
2: {Strongly Correlated Chern Insulators in Magic-Angle Twisted Bilayer Graphene} (key: Yazdani2022) (occur: 1)
Treat these as duplicates? (yes/no) yes
Enter the number of the key to keep: 2

All occurrences of 'YazdaniChern' in chap2/chap2.tex have been replaced with 'Yazdani2022'.

...
# repeat this many times
...

Done cleaning duplicates!
```

# Note
- Backup your data before using this file, preferably using a version control software, so that it is easy to fix mistakes!
- You might want to try out other solutions as well:
  - For renaming cietkey in `.tex` files, you might try [this](https://github.com/dmpalyvos/bibtex-rename).
  - For tidying `.bib` files, [this](https://github.com/FlamingTempura/bibtex-tidy) looks useful.
- I also implemented a helper function `check_arXiv` for listing `.bib` entries that only have arXiv reference. Might be useful if you want to update your file.
