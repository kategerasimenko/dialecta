from pympi import Eaf

from corpora.utils.db_utils import SENTENCE_COLLECTION
from corpora.utils.elan_utils import (
    ANNOTATION_OPTION_SEP, STANDARTIZATION_REGEX,
    STANDARTIZATION_NUM_REGEX, ANNOTATION_NUM_REGEX,
    clean_transcription, get_tier_alignment,
    get_annotation_alignment
)


def process_one_annotation(orig, standartization, annotation):
    words = []

    standartizations = get_annotation_alignment(standartization, num_regex=STANDARTIZATION_NUM_REGEX)
    annotations = get_annotation_alignment(annotation, num_regex=ANNOTATION_NUM_REGEX)

    for i, word in enumerate(clean_transcription(orig).split()):
        word_dict = {'transcription': word.lower()}

        std = standartizations.get(i)
        if std is not None:
            word_dict['standartization'] = std.lower()

        anns = annotations.get(i)
        if anns is not None:
            anns = anns.lower().split(ANNOTATION_OPTION_SEP)
            word_dict['annotations'] = [
                {'lemma': ann.split('-')[0], 'tags': ann.split('-')[1:]}
                for ann in anns
            ]

        words.append(word_dict)

    return words


def process_one_tier(eaf_filename, audio_filename, dialect, speaker, tier_name, orig_tier, standartization_tier, annotation_tier):
    sentences = []
    tier_alignment = get_tier_alignment(orig_tier, standartization_tier, annotation_tier)
    for (start, end), (orig, standartization, annotation) in tier_alignment.items():
        sentence = {
            'words': process_one_annotation(orig, standartization, annotation),
            'dialect': dialect,
            'elan': eaf_filename,
            'speaker': speaker,
            'tier': tier_name,
            'audio': {
                'file': audio_filename,
                'start': start,
                'end': end
            }
        }
        sentences.append(sentence)

    return sentences


def process_one_elan(eaf_filename, audio_filename, dialect):
    eaf_obj = Eaf(eaf_filename)
    sentences = []

    for tier_name, tier in eaf_obj.tiers.items():
        standartization_tier_name = STANDARTIZATION_REGEX.search(tier_name)
        if standartization_tier_name is None:
            continue

        speaker_tier = standartization_tier_name.group(1)
        try:
            orig_tier = sorted(eaf_obj.get_annotation_data_for_tier(speaker_tier), key=lambda x: x[0])
            standartization_tier = sorted(eaf_obj.get_annotation_data_for_tier(tier_name), key=lambda x: x[0])
            annotation_tier = sorted(eaf_obj.get_annotation_data_for_tier(speaker_tier + '_annotation'), key=lambda x: x[0])
        except KeyError:
            print('ERROR: ' + eaf_filename + ': lacking tiers for ' + speaker_tier)
            continue

        speaker = eaf_obj.tiers[speaker_tier][2]['PARTICIPANT'].title()
        tier_sentences = process_one_tier(
            eaf_filename, audio_filename, dialect, speaker, speaker_tier,
            orig_tier, standartization_tier, annotation_tier)
        sentences.extend(tier_sentences)

    return sentences


def insert_sentences_in_mongo(sentences):
    SENTENCE_COLLECTION.insert_many(sentences)