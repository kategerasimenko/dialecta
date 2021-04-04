import re
from lxml import etree
from .annotation_menu import annotation_menu


def get_participant_status(tier_name):
    if '_i_' in tier_name:
        return 'inwr'
    elif '_n_' in tier_name:
        return 'inwd'
    return ''


def get_audio_annot_div(stttime, endtime):
    return '<div class="audiofragment" starttime="%s" endtime="%s"><button class="fa fa-spinner off"></button></div>' % (stttime, endtime)


def get_audio_link(audio_file_path):
    return '<audio id="elan_audio" src="/media/%s" preload></audio>' % audio_file_path


def prettify_transcript(transcript):
    if not transcript[-1].strip():
        transcript = transcript[:-1]

    new_transcript = ''
    tokens_lst = re.split('([ ])', transcript)

    for el in tokens_lst:
        el = el.strip()
        if not el:
            continue

        if el in ['...', '?', '!']:
            new_el = '<tech>%s</tech>' % el

        elif el[-1] in ['?', '!']:
            new_el = '<token><trt>%s</trt></token><tech>%s</tech>' % (el[:-1], el[-1])

        elif '[' in el and ']' in el:
            new_el = ''

            for el_2 in re.split(r'[\[\]]', el):  # splitting [ ]
                if not re.match('[a-zA-Z]', el_2):
                    continue  # removing non-alphabetic values

                if 'unint' in el_2 or '.' in el_2:
                    new_el += '<note>%s.</note>' % el_2.strip('.')
                else:
                    new_el += '<token><trt>%s</trt></token>' % el_2

        else:
            new_el = '<token><trt>%s</trt></token>' % el

        new_transcript += new_el

    return new_transcript


def add_annotation_to_transcript(transcript, normz_tokens_dict, annot_tokens_dict):
    i = 0
    transcript_obj = etree.fromstring('<c>'+transcript+'</c>')

    for tag in transcript_obj.iterchildren():
        if tag.tag != 'token':
            continue

        if i in annot_tokens_dict.keys():
            raw_morph_tags_full = annot_tokens_dict[i][1].split('/')
            morph_tags_full = '/'.join(
                annotation_menu.override_abbreviations(x, is_lemma=True)
                for x in raw_morph_tags_full
            )  # DB
            tag.insert(0, etree.fromstring('<morph_full style="display:none">' + morph_tags_full + '</morph_full>'))

            moprh_tags = raw_morph_tags_full[0].split('-', 1)[1]
            morph_tags = annotation_menu.override_abbreviations(moprh_tags)  # DB
            tag.insert(0, etree.fromstring('<morph>' + morph_tags + '</morph>'))

            lemma_full = annot_tokens_dict[i][0]
            tag.insert(0, etree.fromstring('<lemma_full style="display:none">' + lemma_full + '</lemma_full>'))

            lemma = lemma_full.split('/')[0]
            tag.insert(0, etree.fromstring('<lemma>' + lemma + '</lemma>'))

        if i in normz_tokens_dict.keys():
            tag.insert(0, etree.fromstring('<nrm>' + normz_tokens_dict[i][0] + '</nrm>'))

        i += 1

    return etree.tostring(transcript_obj)[3:-4].decode('utf-8')


def get_annot_div(tier_name, dialect, participant, transcript, normz_tokens_dict, annot_tokens_dict):
    transcript = prettify_transcript(transcript)
    if annot_tokens_dict:
        transcript = add_annotation_to_transcript(transcript, normz_tokens_dict, annot_tokens_dict)

    participant_div = '<span class="participant">%s</span>' % participant
    transcript_div = '<span class="transcript">%s</span>' % transcript
    annot_div = '<div class="annot" tier_name="%s", dialect="%s">%s%s</div>' % (tier_name, dialect, participant_div, transcript_div)

    return annot_div
