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


* Initial vcf upload:
    - `POST /api/upload`.
    - Required params:
        - 'file' (attached multipart form).
        - 'user_id' (int)

    - Example: `/api/upload`
    - Return:
    - ```
        {
            {'job_id': 123 }
        }
      ```


* Job API:
    - `GET /api/jobs`
    - Required: user_id (int)
    - Optional: job_id (int)


    - Default gets all the jobs for a user_id

    - Response for all `/api/jobs?user_id=123`:
    - ```
        {
        results: [
                {
                    id: 1,
                    pubmedarticles: [ ],
                    timestamp: "Sat, 12 May 2018 09:00:21 GMT",
                    user_id: 123,
                    variants: [ ]
                }
            ]
        }
      ```

      - Response for one job: `/api/jobs?user_id=123&job_id=1`
      - ```
      {
        job: {
            id: 1,
            pubmedarticles: [ ],
            timestamp: "Sat, 12 May 2018 09:00:21 GMT",
            user_id: 123,
            variants: [ ]
        }
      }
      ```



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


