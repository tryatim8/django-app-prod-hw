from django.forms import Form, FileField

class ImportCSVForm(Form):
    csv_file = FileField()
