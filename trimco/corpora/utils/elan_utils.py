import re
import os
from pympi import Eaf, Elan


# TODO: join all funcs in ElanObject and use it everywhere


ANNOTATION_WORD_SEP = '|'
ANNOTATION_OPTION_SEP = '/'

STANDARTIZATION_REGEX = re.compile(r'^(.+?)_standartization$')
STANDARTIZATION_NUM_REGEX = re.compile(r'^(\d+):(.+)')
ANNOTATION_NUM_REGEX = re.compile(r'(\d+?):.+?:(.+)')


class Tier:
    def __init__(self, name, info):
        self.name = name
        self.aligned_annotations = info[0]
        self.reference_annotations = info[1]
        self.attributes = info[2]
        self.ordinal = info[3]

        self.top_level = False
        if 'PARENT_REF' not in self.attributes.keys():
            self.top_level = True

        self.side = None
        if '_i_' in self.name:
            self.side = 'interviewer'
        elif '_n_' in self.name:
            self.side = 'speaker'


class ElanObject:
    def __init__(self, path_to_file):
        self.path = path_to_file
        self.Eaf = Eaf(path_to_file)
        self.Eaf.clean_time_slots()
        self.load_tiers()
        self.load_annotation_data()
        self.load_participants()

    def load_participants(self):
        participants_lst = []

        for tier_obj in self.tiers_lst:
            try:
                p_title = tier_obj.attributes['PARTICIPANT'].title()
                if p_title not in participants_lst:
                    participants_lst.append(p_title)
            except KeyError:
                pass

        self.participants_lst = participants_lst

    def load_tiers(self):
        tiers_lst = []
        for tier_name, tier_info in self.Eaf.tiers.items():
            tiers_lst.append(Tier(tier_name, tier_info))
        self.tiers_lst = sorted(tiers_lst, key=lambda data: data.ordinal)

    def load_annotation_data(self):
        annot_data_lst = []
        for tier_obj in self.tiers_lst:
            if tier_obj.top_level:
                for annot_data in self.Eaf.get_annotation_data_for_tier(tier_obj.name):
                    annot_data_lst.append(annot_data + (tier_obj.name,))
        self.annot_data_lst = sorted(annot_data_lst, key=lambda data: data[0])

    def get_tier_obj_by_name(self, tier_name):
        for tier_obj in self.tiers_lst:
            if tier_obj.name == tier_name:
                return tier_obj
        return None

    def add_extra_tags(self, parent_tier_name, start, end, value, typ):
        if typ == 'annotation':
            tier_name = parent_tier_name + '_annotation'
            ling = 'tokenz_and_annot'
        elif typ == 'standartization':
            tier_name = parent_tier_name + '_standartization'
            ling = 'stndz_clause'
        else:
            return

        if self.get_tier_obj_by_name(tier_name) is None:
            self.Eaf.add_tier(tier_name, ling=ling, parent=parent_tier_name)
            self.load_tiers()

        try:
            self.Eaf.remove_annotation(tier_name, (start + end) / 2, clean=True)
        except KeyError:
            pass

        self.Eaf.add_annotation(tier_name, start, end, value)

    def save(self):
        self.Eaf.clean_time_slots()
        try:
            os.remove(self.path + '.bak')
        except OSError:
            pass

        Elan.to_eaf(self.path, self.Eaf, pretty=True)
        os.remove(self.path + '.bak')


def clean_transcription(transcription):
    return re.sub(r'\.\.\.|\?|\[|]|\.|!|un\'?int\.?', '', transcription).strip()


def get_tier_alignment(orig_tier, standartization_tier, annotation_tier):
    tier_alignment = {(ann[0], ann[1]): [ann[2], None, None] for ann in orig_tier}

    for ann in standartization_tier:
        if (ann[0], ann[1]) in tier_alignment:
            tier_alignment[(ann[0], ann[1])][1] = ann[2]

    for ann in annotation_tier:
        if (ann[0], ann[1]) in tier_alignment:
            tier_alignment[(ann[0], ann[1])][2] = ann[2]

    return tier_alignment


def get_annotation_alignment(annotation, num_regex):
    annotations = {}
    if annotation is not None:
        for ann in annotation.split(ANNOTATION_WORD_SEP):
            ann_num, ann = num_regex.search(ann).groups()
            annotations[int(ann_num)] = ann
    return annotations