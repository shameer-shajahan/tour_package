from django import forms
from .models import Packager, TourPackage

class PackagerForm(forms.ModelForm):
    class Meta:
        model = Packager
        fields = [
            'company_name',
            'company_description',
            'location',
            'logo',
            'contact_email',
            'contact_phone',
            'website',
            'established_year',
            'license_number'
        ]

# Create a separate form for TourPackage



from django import forms
from .models import TourPackage

class TourPackageForm(forms.ModelForm):
    class Meta:
        model = TourPackage
        fields = '__all__'
