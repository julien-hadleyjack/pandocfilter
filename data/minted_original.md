# Example 1

```{language=python}
def hello_world():
  print("Hello World!")
```

# Example 2

```{language=python caption="Example for Python 3.6"}
def hello_world(name="World"):
  print(f"Hello {name}!")
```

# Example 3

```python
def hello_world(name="World"):
  print(f"Hello {name}!")
```

# Example 4

Some text with `a inline code block`.

# Example 5

A inline code block with bash highlighting: `echo "$HOME"`{.minted language=bash}.

# Example 6

A inline code block `with options`{escapeinside="||"}.

# Example 7

```
This is a text block.
```

# Example 8

If you want to use code blocks for other filters you need to set the `minted-class` variable. Some default exceptions were already set (i.e. `.table`).

```{.table
    file="results.csv"
    caption="Test Results"}
```
