import hashlib
import magic

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat
from django.conf import settings

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *

from autofill.models import AutoFill
from samples.models.sample import Sample, Upload
from samples.forms_constants import *

class SampleSubmissionForm(forms.ModelForm):
    sequencing_platform = forms.ChoiceField(
        choices = CHOICES['sequencing_platform'],
        required = False,
    )
    host_health = forms.ChoiceField(choices=CHOICES['host_health'],
                                    required = False,)
    host_gender = forms.ChoiceField(choices=CHOICES['host_gender'],
                                    required = False,)
    source = forms.ChoiceField(choices=CHOICES['source'],
                               required = False,)
    
    class Meta:
        model = Sample
        fields = SUBMISSION_FIELDS
        labels = SUBMISSION_LABELS
        widgets = SUBMISSION_WIDGETS

    def _query_autofill(self, user_id):
        query = AutoFill.objects.all().filter(user_id=user_id)
        self.saved_settings = {}
        for row in query:
            if row.field in FIELDS:
                self.saved_settings[row.field] = row.value

    def __init__(self, user_id, *args, **kwargs):
        self._query_autofill(user_id)
        super(SampleSubmissionForm, self).__init__(*args, **kwargs)
        self.fields['sequence_file'] = forms.FileField(
            label='Compressed (bzip2, gzip, zip) FASTQ File',
        )

        for field in self.fields:
            if field in self.saved_settings:
                self.initial[field] = self.saved_settings[field]        
        
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_id = 'submit-sample'
        self.helper.form_class = ''
        self.helper.form_action = ''
        self.helper.layout = Layout()
        
        self.helper.layout.extend(self.fields)
        
        offset = 'col-sm-offset-2 col-md-offset-3'
        tab_css = 'col-sm-8 col-md-6 ' + offset
        self.helper.layout.insert(0, 'Project Information')
        self.helper[0:9].wrap_together(Tab, css_class=tab_css)
        self.helper.layout.insert(1, 'Publication Information')
        self.helper[1:7].wrap_together(Tab, css_class=tab_css)
        self.helper.layout.insert(2, 'Organism Information')
        self.helper[2:13].wrap_together(Tab, css_class=tab_css)
        self.helper.layout.insert(3, 'Phenotype Information')
        self.helper[3:15].wrap_together(Tab, css_class=tab_css)
        self.helper.layout.insert(4, 'Sequence Information')
        self.helper[4:8].wrap_together(Tab, css_class=tab_css)

        self.helper[0:5].wrap_together(TabHolder)
        self.helper.add_input(Submit('submit', 'Submit Sample', css_class=offset))
        
    def save_upload(self, sample_id, FILES, *args, **kwargs):
        upload = Upload(sample_id=sample_id, path=FILES['sequence_file'], 
                        md5sum=self.file_md5sum)
        return upload.save()
        
    def clean_sequence_file(self):
        file = self.cleaned_data['sequence_file']
        try:
            if file._size > MAX_FILE_SIZE:
                    raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(MAX_FILE_SIZE), filesizeformat(file._size)))
            else:
                content_type = ''
                md5sum = ''
                if hasattr(file, 'temporary_file_path'):
                    content_type = self.content_type_from_file(file.temporary_file_path())
                    md5sum = self.md5sum(file.temporary_file_path())
                else:
                    content_type, md5sum = self.content_type_and_md5sum_from_memory(file)
            
                if content_type in ACCEPTED_FILETYPES:
                    query = Upload.objects.filter(md5sum=md5sum)
                    self.file_md5sum = md5sum
                    if query.count():
                        raise forms.ValidationError(_('A file with MD5sum (%s) has already been uploaded.') % (md5sum))
                else:
                    raise forms.ValidationError(_('Filetype not supported.'))
        except AttributeError:
            pass        

        return file

    
    def content_type_and_md5sum_from_memory(self, file):
        content_type = ''
        md5 = hashlib.md5()
        file.open()
        for chunk in iter(lambda: file.read(128*md5.block_size), b''):
            if not content_type:
                content_type = magic.from_buffer(chunk, mime=True)
            md5.update(chunk)
        file.close()
        
        return [content_type, md5.hexdigest()]
     
    def content_type_from_file(self, file):
        fh = open(file)
        content_type = magic.from_buffer(fh.read(1024), mime=True)
        fh.close()
        
        return content_type
        
    def md5sum_from_file(self, file):
        md5 = hashlib.md5()
        fh = open(file)
        for chunk in iter(lambda: fh.read(128*md5.block_size), b''): 
            md5.update(chunk)
        fh.close()
        
        return md5.hexdigest()