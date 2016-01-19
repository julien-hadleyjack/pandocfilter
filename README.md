# Collection of custom pandoc filters

| Name   | Description                                                               |
|--------|---------------------------------------------------------------------------|
| minted | Converts code blocks from listings environment to minted for LaTeX output |

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


# Generate test output

For testing purposes a Markdown document is converted to latex using pandoc and the filters. The steps for this conversion are:

1. `_original.md`: The original Markdown document
2. `_original.json`: The internal structure of the original documentation represented in JSON
3. `_result.json`: The internal structure of the document after applying the filter
4. `_result.tex`: The final conversion into the LaTeX document

All these steps are automated using the `create_files.sh` script. Just run the script with the prefix of the markdown documents as an argument (i.e. `data/create_files.sh minted`).