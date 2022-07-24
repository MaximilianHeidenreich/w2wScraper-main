
# Installation
- python3 -m pip install bs4
- python3 -m pip install requests
- python3 -m pip install tqdm 


# Architecture

Module:

## Fetcher
Input: URL, optional query params
Fetches a given webpage and returns DOM representaton

## Transformer
### Operations
- stripOuterWhitespace
- toInt

## Extractor
### Operations
- querySelector
- querySelectorAll
- text

## Mapper
Returns