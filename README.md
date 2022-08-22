# Hyde Static Site Generator

**Hyde** is a static site generator in the vein of [Jekyll](https://jekyllrb.com/), but with some key differences:
* Written in Python, for ease and extendability
* Not so blog-oriented

## Core Concepts

Hyde takes an input of a "site", represented and files and folders, does some processing, and writes them to the *site destination*. A site definition is currently only a different folder, but with plans to extend this to write directly to S3 or other services related to static site hosting. Hyde treats all text files as [Liquid](https://shopify.github.io/liquid/) templates, everything else is written as-is. All folders starting with `_` are ignored for site generation, except those with special meaning.

### Data

All YAML files with the `.yaml` extension in the `_data` folder are read and made available for site generation. It can be accessed via the `data.<name of file without extension>` variable. 

### Templates

Templates can include all Liquid tags, filters, and other functionality that [python-liquid](https://pypi.org/project/python-liquid/) supports. Templates can optionally include front matter, as delimited by YAML separators `---`. The front matter is YAML data that can be accessed by the `page` variable in the template.

Front matter templates should be in the following format:
```yaml
---
# YAML-formatted data goes here
---
<!-- template goes here -->
```

### Layouts

Layouts are special templates that can wrap another template. This is useful to standardize the HTML used by lots of pages. The layout templates are HTML files with the `.html` extension put in the `_layouts` folder. Normal templates can use the layout by putting the special `$layout` field in the front matter. Layout templates can reference the same `page` variable as the enclosed template.

## Installation

```commandline
gh repo clone lylesmatt/HydeStaticSiteGenerator # or otherwise check out the repo
cd HydeStaticSiteGenerator
pip install -e .
```

## Getting Started

As part of the installation, a command line tool `hyde` is included. It currently includes the following commands:
1. `build` generate the site, at the current folder
1. `clean` delete the generated site, based on the current folder