"""
Useful functions associated with sequence.

To use:
from sequence.tools import UTIL1, UTIL2, etc...
"""
import json

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.management.base import CommandError

from staphopia.utils import read_json, timeit
from sample.models import Flag
from sequence.models import Stage, Summary


def get_stages():
    stages = {}
    for stage in Stage.objects.all():
        stages[stage.name] = stage
    return stages


@transaction.atomic
def create_stage(name):
    stage = None
    try:
        stage = Stage.objects.create(name=name)
    except IntegrityError as e:
        raise CommandError(f'Unable to create stage {name}. Error: {e}')
    return stage


@timeit
@transaction.atomic
def insert_sequence_stats(sample, version, files, force=False):
    """Insert seqeunce quality metrics into database."""
    if force:
        delete_stats(sample, version)

    is_paired = False
    if 'fastq_r2' in files:
        is_paired = True

    stages = get_stages()
    stat_objects = []
    stats = ['fastq_adapter', 'fastq_cleanup', 'fastq_ecc', 'fastq_original']
    flag_sample = False
    for stat in stats:
        stage_name = stat.split('_')[1]
        stage = None
        if stage_name in stages:
            stage = stages[stage_name]
        else:
            stage = create_stage(stage_name)

        json_data = read_json(files[stat])
        rank = __get_rank(json_data["qc_stats"], is_paired)
        if not rank and stat == 'fastq_cleanup':
            flag_sample = True

        stat_objects.append(Summary(
            sample=sample,
            version=version,
            stage=stage,
            is_paired=is_paired,
            rank=rank,
            read_lengths=json.dumps(json_data["read_lengths"], sort_keys=True),
            qual_per_base=json.dumps(json_data["per_base_quality"],
                                     sort_keys=True),
            **json_data["qc_stats"]
        ))

    if flag_sample:
        print(f'{sample.name}: Flagging for less than 20x coverage.')
        Flag.objects.get_or_create(sample=sample, reason='coverage < 20x')
        sample.is_flagged = True
        sample.save()

    try:
        Summary.objects.bulk_create(stat_objects, batch_size=5)
        print(f'Inserted sequence stats for {sample.name} ({sample.id})')
    except IntegrityError as e:
        raise CommandError(' '.join([
            f'Unable to insert stats for {sample.name} ({sample.id}).',
            f'Please use --force to update stats. Error: {e}'
        ]))


@transaction.atomic
def delete_stats(sample, version):
    """Force update, so remove from table."""
    print("Force used, emptying FASTQ related results.")
    Summary.objects.filter(sample=sample, version=version).delete()


def __get_rank(data, is_paired):
    """
    Determine the rank of the reads.

    3: Gold, 2: Silver, 1: Bronze, 0: <20x coverage, flag this sample
    """
    rank = None
    if data['coverage'] < 20:
        rank = 0
    elif not is_paired:
        rank = 1
    elif data['read_mean'] >= 95:
        if data['qual_mean'] >= 30:
            if data['coverage'] >= 100:
                rank = 3
            elif data['coverage'] >= 50:
                rank = 2
            else:
                rank = 1
        else:
            rank = 1
    else:
        rank = 1

    return rank
