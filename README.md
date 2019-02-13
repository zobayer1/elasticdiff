# ElasticDiff

### Version 0.1.0

A python command line application for calculating document differences between two elasticsearch indices.
The application has extremely small memory footprint and the only bottleneck is the reading speed from
elasticsearch indices.

## Getting Started

### Key Technologies

* Redis - For extremely fast hash lookup
* Elasticsearch - Document storage

### Prerequisites

* Python 3.6+
* Install [requirements](./requirements.txt) using `pip install -r requirements.txt`

### Configuration

A sample json [configuration](./conf.json) file:

```
{
  "elastic": {
    "source": {
      "host": "192.168.5.127",
      "port": 9200,
      "index": "lesson_catalog",
      "type": "lesson"
    },
    "target": {
      "host": "192.168.5.127",
      "port": 9200,
      "index": "lesson_catalog_bk",
      "type": "lesson"
    },
    "include_id": true,
    "scroll_size": 1000,
    "scroll_time": "1m"
  },
  "redis": {
    "host": "localhost",
    "port": 6379,
    "id": 0,
    "password": "T9rwf2128"
  }
}
```

### Running the Script

Run `elasticdiff.py` with a configuration json file passed with `-c` or `--config` switch

Example: `python elasticdiff.py -c conf.json`

### Sample output

* When there are mismatches:
```
('lesson_catalog_bk', 'lesson', 'AWjmTKn_UiR_GHoFe_wq')
('lesson_catalog', 'lesson', 'AWjmTKn_UiR_GHoFe_wq')
Total 2 record(s) mismatched
```
* Otherwise:
```
Total 0 record(s) mismatched
```

## Caveats

### How is it done?

Documents from each index are scrolled in parallelly. As documents are being scrolled in, they are recursively sorted
before serialization and MD5 hash for each document is calculated. A inverted lookup index is built using redis with
(document hash, document id) as (key, value) pairs. This allows finding the number of document ids that get matched
to one single document.

### How does ordering work?

Since the documents are basically JSON data, there are no specific order. So before calculating hash, a document must
be ordered in a predictable and consistent way. One brilliant way to do so is to recursively sort the document and then
serialize it. Following code snippet shows how the sorting is performed:
```
def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj
```

### Why MD5 Hashing?

We are not concerned about security here. Even for a several billion documents, the probability of two different documents
resulting in the same MD5 sum is almost 0. Also, MD5 is the fastest among the most well known hashing algorithms.

### Why not Parallelizing Hash Computation?

The real bottleneck in this system is the reading speed from Elasticsearch indices. Using a Executor Thread Pool will
impose startup overheads and collecting the results will also add some delays. A pool of 8 workers showed no improvements
in performance.

### How is Memory Overhead?

This application has virtually 0 memory overhead. No buffer memory has been used to even temporarily store data. Python
generators are used to ensure minimum buffer loads.

### What are the Limitations?

* Inherits all the disadvantages of Elasticsearch Scroll API.
* Does not work between same indices from same node.
* Has a room to become a lot more configurable.

## Author

* **ZOBAYER HASAN** - *Primary Implementation* - (zobayer1@gmail.com)
