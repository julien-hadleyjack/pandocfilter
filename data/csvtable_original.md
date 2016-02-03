# Example 1

```{.table
    file="data/csvtable_example1.csv"
    header=yes}
```

# Example 2

```{.table
    file="https://raw.githubusercontent.com/julien-hadleyjack/pandocfilter/master/data/csvtable_example1.csv"
    header=yes}
```

# Example 3

```{.table header=yes}
Header 1, Header 2
Text 1,Text 2
Text 3,Text 4
```

# Example 4

| Header 1 | Header 2 |
|----------|----------|
| Text 1   | Text 2   |
| Text 3   | Text 4   |

# Example 5

| **Header 1**    | Header 2 | Header 3 |
|-----------------|----------|----------|
| Text 1[@source] | Text 2   | Text 3   |
| Text 4          | Text 5   | Text 6   |

# Example 6

```{.table header=yes}
**Header 1**, Header 2
Text 1[@source],Text 2
Text 3,Text 4
```

# Example 6

```{.table header=yes align="RL"}
Header 1, Header 2
Text 1,Text 2
Text 3,Text 4
```

# Example 7

```{.table header=yes width="0.4 0.6"}
Header 1, Header 2
Text 1,Text 2
Text 3,Text 4
```

# Example 8

```{.table
    file="data/csvtable_example2.csv"
    delimiter=;
    header=yes}
```

# Example 9

```{.table
    file="data/csvtable_example1.csv"
    content_pos=bottom
    header=yes}
Text 5,Text 6
```

# Example 10

```{.table
    file="data/csvtable_example1.csv"
    quote_char=|
    header=yes}
|New Header 1|,New Header 2
```

# Example 11

```{.table delimiter="|"}
Header 1 | New Header 2 | Header 3 | Header 4
Text 1   | Text 2       | Text 3   | Test 4
```

# Example 12

| Header 1 | Header 2 |
|----------|----------|
| Text 1   | Text 2   |
| Text 3   | Text 4   |

Table: This is a table caption 

# Example 13

```{.table
    file="data/csvtable_example1.csv"
    caption="This is a table caption"
    header=yes}
```