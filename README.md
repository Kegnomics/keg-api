# Kegnomigs API

This serves the following purposes:

* pubmed querying based on keywords
* parsing of top variants and getings some keywords from that as well
* filtering the large number of variants that are created after the initial run on the vcf file


## API Design

* Root: `/api`
* Pubmed queries:
    - `GET /api/pubmed`.
    - Required params: 'keywords' (comma separated strings).
    - Optional params: 'maxres' (int)
    - Example: `/api/pubmed?keywords=cleft,palate&maxres=2`



### Fields

#### 1. Variants API

* id (rsid)
* locus
* outcome (benign, possibly pathogenic)
* fenotype
* frequency
* SIFT score
* polyphene score
* gene


