from django.contrib import admin

from django.db import transaction
from django.conf.urls import url
from django.template.context import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from corpora.models import *
from corpora.utils.elan_tools import standartizator, Standartizator, elan_to_html
from corpora.utils.word_list import insert_manual_annotation_in_mongo

import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from reversion.admin import VersionAdmin


@admin.register(Recording)
class RecordingAdmin(VersionAdmin):

    list_display = ('string_id', 'audio','speakerlist', 'title', 'auto_annotated', 'checked')
    search_fields = ('to_speakers__string_id',)
    list_max_show_all = 500
    list_per_page = 200
    filter_horizontal = ('to_speakers', 'to_interviewers')

    editor_template = 'editor.html'
    trainer_template = 'trainer.html'
    fields = (
        'string_id',
        ('audio','data'),
        ('edit_transcription', 'annotate_transcription'),
        ('auto_annotated', 'checked'),
        ('recording_date', 'recording_time', 'recording_place'),
        'file_check',
        ('audio_data', 'participants'),
        'to_speakers',
        'to_interviewers',
        'speakerlist',
        'title',
        'topics',
        'comments',
        'metacomment1',
        ('metacomment2', 'metacomment3'),
        'to_dialect',
        'recording_device',
    )
    readonly_fields = (
        'audio_data',
        'participants',
        'speakerlist',
        'file_check',
        'edit_transcription',
        'annotate_transcription'
    )

    save_as = True

    class Media:
        js = ("js/ustie_id.js",)

    def speakerlist(self, obj):
        return ', '.join([a.string_id for a in obj.to_speakers.all()])

    def get_urls(self):
        self.processing_request = False
        urls = super(RecordingAdmin, self).get_urls()
        my_urls = [
            url(r'\d+/edit/$', self.admin_site.admin_view(self.edit)),
            url(r'\d+/auto/$', self.admin_site.admin_view(self.auto_annotate)),
            url(r'\d+/train/$', self.admin_site.admin_view(self.train)),
            url(r'^ajax/$', self.ajax_dispatcher, name='ajax'),
        ]
        return my_urls + urls

    @transaction.atomic
    def edit(self, request):
        self.recording_obj = get_object_or_404(Recording, id=request.path.split('/')[-3])
        self.elan_converter = elan_to_html(self.recording_obj)
        self.elan_converter.build_page()

        # print(self.recording_obj.model_to_normalize)
        self.new_standartizator = Standartizator(self.recording_obj.to_dialect)
        self.standartizator = standartizator(self.recording_obj.to_dialect)
        self.standartizator.start_standartizator()

        annot_menu_select, annot_menu_checkboxes = self.elan_converter.build_annotation_menu()
        
        context = {
            'ctext': self.elan_converter.html,
            'audio_path': self.recording_obj.audio.name,
            'media': self.media['js'],
            'annot_menu_select' : annot_menu_select,
            'annot_menu_checkboxes' : annot_menu_checkboxes,
        }
        return render_to_response(self.editor_template, context_instance=RequestContext(request, context))

    @transaction.atomic
    def auto_annotate(self, request):
        self.recording_obj = get_object_or_404(Recording, id=request.path.split('/')[-3])
        self.elan_converter = elan_to_html(self.recording_obj, mode='auto-annotation')
        self.elan_converter.build_page()

        annot_menu_select, annot_menu_checkboxes = self.elan_converter.build_annotation_menu()
        
        context = {
            'ctext': self.elan_converter.html,
            'audio_path': self.recording_obj.audio.name,
            'media': self.media['js'],
            'annot_menu_select' : annot_menu_select,
            'annot_menu_checkboxes' : annot_menu_checkboxes,
        }
        return render_to_response(self.editor_template, context_instance=RequestContext(request, context))

    @transaction.atomic
    def train(self, request):
        self.recording_obj = get_object_or_404(Recording, id=request.path.split('/')[-3])
        self.elan_converter = elan_to_html(self.recording_obj, 'orth_trainig')
        
        self.standartizator = standartizator(self.recording_obj.to_dialect)
        self.standartizator.start_standartizator()
        
        context = {
            'ctext': self.elan_converter.html,
            'audio_path': self.recording_obj.audio.name,
            'media': self.media['js'],
            'examples_dict': json.dumps(self.standartizator.examples_dict),
            'exceptions_lst': json.dumps(self.standartizator.exceptions_lst),
        }
        return render_to_response(self.trainer_template, context_instance=RequestContext(request, context))

    @csrf_exempt
    def ajax_dispatcher(self, request):
        response = {}
        self.processing_request = True

        if request.POST['request_type'] == 'save_model_req':
            self.standartizator.update_model(
                json.loads(request.POST['request_data[trd]']),
                json.loads(request.POST['request_data[exr]']),
            )

        elif request.POST['request_type'] == 'training_data_load_req':
            response['training_dict'] = self.standartizator.examples_dict

        elif request.POST['request_type'] == 'trt_annot_req':
            if request.POST['request_data[mode]'] == 'manual':
                manual_words = self.new_standartizator.get_manual_standartizations(request.POST['request_data[trt]'])
                response['result'] = manual_words or [request.POST['request_data[nrm]']]

            elif request.POST['request_data[mode]'] == 'auto':  # TODO: move this to new standartizator
                response['result'] = self.standartizator.auto_annotation(request.POST['request_data[trt]'])

        elif request.POST['request_type'] == 'annot_suggest_req':
            ann = [request.POST['request_data[trt]'], request.POST['request_data[nrm]']]
            response['result'] = self.new_standartizator.get_annotation_options_list(ann)

        elif request.POST['request_type'] == 'save_elan_req':
            self.elan_converter.save_html_to_elan(request.POST['request_data[html]'])

        elif request.POST['request_type'] == 'save_annotation':
            insert_manual_annotation_in_mongo(
                model=str(self.new_standartizator.model),
                word=request.POST['request_data[trt]'],
                standartization=request.POST['request_data[nrm]'],
                lemma=request.POST['request_data[lemma]'],
                grammar=request.POST['request_data[annot]']
            )

        return HttpResponse(json.dumps(response))


@admin.register(Corpus)
class CorpusAdmin(VersionAdmin):
    pass
