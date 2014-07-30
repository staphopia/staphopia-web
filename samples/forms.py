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
from samples.models import Sample, MetaData, Upload
from samples.forms_constants import *

class SampleMetaDataForm(forms.Form):

    def _query_autofill(self, user_id):
        query = AutoFill.objects.all().filter(user_id=user_id)
        self.saved_settings = {}
        for row in query:
            if row.field in FIELDS:
                self.saved_settings[row.field] = row.value

    def __init__(self, user_id, *args, **kwargs):
        self._query_autofill(user_id)
        super(SampleMetaDataForm, self).__init__(*args, **kwargs)
        
        for id in FIELD_ORDER:
            value = self.saved_settings[id] if id in self.saved_settings else ''
            widget_attrs = {
                'placeholder':FIELDS[id][1],
                'value':value,
            }
            attributes = {                    
                'label':FIELDS[id][0],            
                'required':True if id in REQUIRED_FIELDS else False,
            }
            if id.endswith('_email'):
                attributes['widget'] = forms.EmailInput(attrs=widget_attrs)
                self.fields[id] = forms.EmailField(**attributes)
            elif id.endswith('_link'):
                attributes['widget'] = forms.URLInput(attrs=widget_attrs)
                self.fields[id] = forms.URLField(**attributes)
            elif id.endswith('_date'):
                attributes['widget'] = forms.DateInput(attrs=widget_attrs)
                self.fields[id] = forms.DateField(**attributes)
            elif id.startswith('is_'):
                if id == 'is_public':
                    widget_attrs['checked'] = 'checked'
                attributes['widget'] = forms.CheckboxInput(attrs=widget_attrs)
                self.fields[id] = forms.BooleanField(**attributes)
            elif id in SELECT_FIELDS:
                attributes['widget'] = forms.Select(attrs=widget_attrs)
                self.fields[id] = forms.ChoiceField(choices=CHOICES[id], 
                                                    initial=value, 
                                                    **attributes)
            elif id == 'sequence_file':
                attributes['widget'] = forms.ClearableFileInput(attrs=widget_attrs)
                self.fields[id] = forms.FileField(**attributes)
            else:
                if id == 'comments':
                    attributes['widget'] = forms.Textarea(attrs=widget_attrs)
                else:
                    attributes['widget'] = forms.TextInput(attrs=widget_attrs)
                self.fields[id] = forms.CharField(**attributes)

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
        
    def create_new_sample(self, user_id, is_public, is_paired, *args, **kwargs):
        new_sample = Sample.objects.create(user_id=user_id, 
                                           is_public=is_public, 
                                           is_paired=is_paired)
        return new_sample

        
    def save_metadata(self, user, sample_id, POST, *args, **kwargs):
        results = []
        
        for field, value in POST.items():
            if field not in POST_IGNORE:
                metadata = MetaData(sample_id=sample_id, field=field, value=value)
                if value:
                    results.append(metadata.save())
                else:
                    results.append('{0} value is empty, did not save.'.format(field))
        
        # Generate sample tag
        num_samples = str(Sample.objects.filter(user_id=user.id).count())
        sample_tag = '{0}_{1}'.format(user.username, num_samples.zfill(6))
        metadata = MetaData(sample_id=sample_id, field='sample_tag', value=value)
        results.append(metadata.save())
        
        return results
        
    def save_upload(self, sample_id, FILES, *args, **kwargs):
        upload = Upload(sample_id=sample_id, upload=FILES['sequence_file'], 
                        upload_md5sum=self.file_md5sum)
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
                    query = Upload.objects.filter(upload_md5sum=md5sum)
                    self.file_md5sum = md5sum
                    if query.count():
                        raise forms.ValidationError(_('A file with MD5sum (%s) has already been uploaded.') % (md5sum))
                else:
                    raise forms.ValidationError(_('Filetype not supported.'))
        except AttributeError:
            pass        

        print self.file_md5sum
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