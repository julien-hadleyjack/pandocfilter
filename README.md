# Collection of custom pandoc filters

This project is a collection of pandoc filters that I created:

| Name                  | Description                              |
|-----------------------|------------------------------------------|
| [minted](#minted)     | Use minted to show code blocks in LaTeX  |
| [csvtable](#csvtable) | Include Content from CSV files as tables |

[pandoc](http://pandoc.org/) is a great tool that can be used to convert between many different formats (HTML, Markdown, restructuredText, LaTeX, Microsoft Word, EPUB, ...). For example you can write a document in Markdown (which make writing text very easy) and format the final result as a LaTeX document (which can produce beautifully formatted documents suitable for print and digital distribution) by using pandoc to convert between the two formats.

pandoc enables you to extend the builtin functionality by [adding filters](http://pandoc.org/scripting.html). Besides [the example ones](https://github.com/jgm/pandocfilters) there are [many different ones](https://github.com/jgm/pandoc/wiki/pandoc-Filters) from the community that provide functionality like [convert svg to pdf](https://gist.github.com/jeromerobert/3996eca3acd12e4c3d40), [automatic numbering of figures](https://github.com/tomduck/pandoc-fignos) and the [generation of diagrams](https://github.com/raghur/mermaid-filter).

To use the filters in this project just clone this repository and install the dependencies:

```shell
git clone https://github.com/julien-hadleyjack/pandocfilter.git
pip install -r pandocfilter/requirements.txt
```

# minted

By default pandoc formats code block using a [custom LaTeX Highlighting environment](https://hackage.haskell.org/package/pandoc-1.9.2/docs/Text-pandoc-Highlighting.html). This is very basic but doesn't depend on many LaTeX packages. If you use the option `--listings`, then the environment provided by the LaTeX package [listings](https://ctan.org/pkg/listings) will be used. I personally like [minted](https://ctan.org/pkg/minted) so I wrote this filter to be able to use instead for the LaTeX output.  

To be able to use minted you need to have [Pygments](http://pygments.org/) installed. It provides support for syntax highlighting of over 300 languages and other text formats. Look at the [minted documentation](https://ctan.org/pkg/minted) to see if all the other requirements are satisfied if you are having problems with compiling the LaTeX output.
 
After installing the requirements for minted and for the filter, you can run it like any other filter:

```shell
pandoc --filter pandocfilter/minted.py --template default.latex input.md -o output.tex
```

You need to use a template that include the minted package with:

```latex
\usepackage{minted}
```

in the pre-ample. You can do it either in your own template or use a modified default template from pandoc. To save the default one run:

```shell
pandoc -D latex > default.latex
```

Now add the line somewhere before the start of the document content (so before `\begin{document}`).


Because minted calls an external program you need to run LaTex with this option:

```shell
latex -shell-escape output.tex
```

The minted documentation warns that this might pose a security risk so use with caution and don't run it on documents with unknown origin.

## Usage

A simple example for a code block that will be converted:

<pre lang="no-highlight"><code>
```{language=python}
def hello_world(name="World"):
  print(f"Hello {name}!")
```
</code></pre>

Result without filter (with listings package):

```latex
\begin{lstlisting}[language=Python]
def hello_world(name="World"):
  print(f"Hello {name}!")
\end{lstlisting}
```

Result with filter (with minted package):

```latex
\begin{minted}[python]{text}
def hello_world(name="World"):
  print(f"Hello {name}!")
\end{minted}
```

### Options

There are some global settings you can configure using the [YAML metadata block](http://pandoc.org/README.html#metadata-blocks) from pandoc:

```
<pre lang="yaml"><code>
---
minted-exclude: [table, diagram]
minted-class: false
---
</code></pre>
Start of the content for the document.
```

#### Global options

The global settings are:

| Name            | Description                                                                                                                                                                                                                                                   |
|-----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| minted-exclude  | Code with this class will not be converted to minted environment. This is done so that code blocks can also be used for other filters like [csvtable](#csvtable). By default code with have one of the classes `table`, `ditaa`, `plantuml` will be ignored. |
| minted-class    | Only convert to the minted environment when the code block has the minted class. This rule only applies to code block and ignores inline code which only uses the `minted-exclude` setting. This setting is false by default.                              |
| minted-language | The default language that is used for syntax highlighting. Default is `text`.                                                                                                                                                                                 |
| minted-figure  | When code should have a caption, then it will be wrapped in a figure environment. With this setting you can configure the positioning of the figure environment. The default value is `H`.                                                                     |

A class in a code block would look like this:

<pre lang="no-highlight"><code>
```{.minted language=python}
def hello_world(name="World"):
  print(f"Hello {name}!")
```
</code></pre>

A class in a inline code block would look like this: <pre lang="no-highlight"><code>`print(f"Hello {name})`{.minted language=python}</code></pre>. The class is `minted` in both cases.

#### Local options

<pre lang="no-highlight"><code>
```{.minted .breaklines .escapeinside="||" language=python caption="Example for Python 3.6"}
def hello_world(name="World"):
  # The |\colorbox{green}{new}| syntax
  print(f"Hello {name}!")
```
</code></pre>

The attributes that will be used are:

| Name          | Description                                                                                                                                                                          |
|---------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| language      | The language that is used for syntax highlighting. See the list of [available lexers](http://pygments.org/docs/lexers/) for Pygmentize to find out the name that you should use. |
| caption       | The text for a caption. (Default: None)                                                                                                                                              |

All further attributes and classes (except `minted`) will be passed onto the minted environment. If that option doesn't exist, then it will produce an error during building of the LaTex document.

# csvtable

# Developing

## Build standalone executable #

You can use [Nuitka](http://nuitka.net/) to translate the filter to a C++ programm and create a standalone executable by running the command:

```shell
nuitka --recurse-all --standalone minted.py
```


## Generate test output #

For testing purposes a Markdown document is converted to latex using pandoc and the filter. The files used/created by this conversion are:

1. `_original.md`: The original Markdown document
2. `_original.json`: The internal structure of the original documentation represented in JSON
3. `_result.json`: The internal structure of the document after applying the filter
4. `_result.tex`: The final conversion into the LaTeX document

All these steps are automated using the `create_files.sh` script. Just run the script with the prefix of the markdown documents as an argument (i.e. `data/create_files.sh minted`).