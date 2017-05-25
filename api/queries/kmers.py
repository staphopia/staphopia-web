"""API utilities for kmer related viewsets."""


def get_kmer_by_string(kmer, samples=None):
    """Query kmer against Elasticsearch cluster."""
    import requests
    from kmer.partitions import PARTITIONS
    child = kmer[-7:]
    table = 'kmer_{0}'.format(PARTITIONS[child].lower())
    url = 'http://localhost:9200/{0}/kmer/{1}/'.format(table, kmer)
    r = requests.get(url)
    json = r.json()
    total = 0
    result = {"results": []}
    if json['found']:
        for sample in json['_source']['samples']:
            sample_id, count = sample.split('-')
            if samples:
                sample_id = int(sample_id.lstrip('0'))
                if sample_id in samples:
                    result['results'].append({
                        "sample_id": sample_id,
                        "count": count
                    })
                    total += 1
            else:
                # Get all samples, only for admins
                return {
                    "has_errors": "MISSING_SAMPLES",
                    "message": "kmer requests must include samples to query"
                }
        result["count"] = total
        return result
    else:
        return json


def get_kmer_by_partition(partition, kmers, samples):
    """Query kmer against Elasticsearch cluster."""
    import requests
    results = []
    url = 'http://localhost:9200/{0}/kmer/_mget/'.format(partition)
    r = requests.post(url, json={"ids": [kmers]})
    json = r.json()
    if json['docs']:
        for index in json["docs"]:
            if index["found"]:
                for sample in index['_source']['samples']:
                    sample_id, count = sample.split('-')
                    sample_id = int(sample_id.lstrip('0'))
                    if sample_id in samples:
                        results.append({
                            "kmer": index['_id'],
                            "sample_id": sample_id,
                            "count": count
                        })
    return results


def get_kmer_by_sequence(sequence, samples):
    """Query kmer against Elasticsearch cluster."""
    import requests
    from kmer.partitions import PARTITIONS
    complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
    k = 31
    kmers = [sequence[i:i + k] for i in range(0, len(sequence)+1-k)]
    tables = {}
    for kmer in kmers:
        child = kmer[-7:]
        table = 'kmer_{0}'.format(PARTITIONS[child].lower())
        if table not in tables:
            tables[table] = []
        tables[table].append(kmer)

        # Reverse complement
        rc_kmer = ''.join(
            [complement[base] for base in kmer][::-1]
        )
        child = rc_kmer[-7:]
        table = 'kmer_{0}'.format(PARTITIONS[child].lower())
        if table not in tables:
            tables[table] = []
        tables[table].append(rc_kmer)

    results = []
    for key, vals in tables.iteritems():
        url = 'http://localhost:9200/{0}/kmer/_mget/'.format(key)
        vals = list(set(vals))
        r = requests.post(url, json={"ids": vals})
        json_data = r.json()
        if json_data['docs']:
            for index in json_data["docs"]:
                if index["found"]:
                    for sample in index['_source']['samples']:
                        sample_id, count = sample.split('-')
                        sample_id = int(sample_id.lstrip('0'))
                        if sample_id in samples:
                            results.append({
                                "kmer": index['_id'],
                                "sample_id": sample_id,
                                "count": count
                            })
    return results
