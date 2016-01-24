# Collection of custom pandoc filters

[Pandoc](http://pandoc.org/) is a great tool that can be used to convert between many different formats (HTML, Markdown, restructuredText, LaTeX, Microsoft Word, EPUB). For example you can write a document in Markdown ()which make writing text very easy) and format the final result as a LaTeX document (which can produce beautifully formatted documents suitable for print and digital distribution).

Pandoc enables you to extend the builtin functionality by [adding filters](http://pandoc.org/scripting.html). Besides [the example ones](https://github.com/jgm/pandocfilters) there are [many different ones] that provide functionality like [convert svg to pdf](https://gist.github.com/jeromerobert/3996eca3acd12e4c3d40), [automatic numbering of figures](https://github.com/tomduck/pandoc-fignos) and the [geration of diagrams](https://github.com/raghur/mermaid-filter).

This project is a collection of filters that I created:

| Name     | Description                              |
|----------|------------------------------------------|
| minted   | Use minted to show code blocks in LaTex  |
| csvtable | Include Content from CSV files as tables |

# minted

Result without filter:

```latex
\begin{lstlisting}[language=Python]
def hello_world(name="World"):
  print(f"Hello {name}!")
\end{lstlisting}
```

Result with filter:

```latex
\begin{minted}[python]{text}
def hello_world(name="World"):
  print(f"Hello {name}!")
\end{minted}
```

# csvtables

# Developing

## Build standalone executable #

You can use [Nuitka](http://nuitka.net/) to translate the filter to a C++ programm and create a standalone executable by running the command:

```shell
nuitka --recurse-all --standalone minted.py
```


## Generate test output #

For testing purposes a Markdown document is converted to latex using pandoc and the filters. The steps for this conversion are:

1. `_original.md`: The original Markdown document
2. `_original.json`: The internal structure of the original documentation represented in JSON
3. `_result.json`: The internal structure of the document after applying the filter
4. `_result.tex`: The final conversion into the LaTeX document

All these steps are automated using the `create_files.sh` script. Just run the script with the prefix of the markdown documents as an argument (i.e. `data/create_files.sh minted`).