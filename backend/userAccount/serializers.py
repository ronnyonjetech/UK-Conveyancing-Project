from rest_framework import serializers
from userAccount.models import NewUser
from pdf_module.models import Conveyance,AnalyzedConveyance
import fitz 

class RegisterUserSerializer(serializers.ModelSerializer):
    """
    Currently unused in preference of the below.
    """
    # email = serializers.EmailField(required=True)
    # user_name = serializers.CharField(required=True)
    # password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = NewUser
        fields = ( 'user_name','location','email','phone_number', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        # as long as the fields are the same, we can just use this
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
# def extractTextFromFiles(file_path):
#         doc = fitz.open(file_path,'r') 
#         text = "" 
#         for page in doc: 
#             text+=page.get_text() 
#         return text

# class PdfSerializer(serializers.ModelSerializer):
#     analyzed_conveyance = AnalyzedSerializer(many=False, read_only=True)
#     class Meta:
#         model=Conveyance
#         fields='__all__'

    # def to_internal_value(self, data):
    #     validated = {
    #             'id':data.get('id'),
    #             'file_name': data.get('file_name'),
    #             'file': data.get('file'),
    #             'user':data.get('user'),
    #             # 'extracted_text': extractTextFromFiles( data.get('file')),
    #             # 'summarized_text':extractTextFromFiles(data.get('file')),   
    #             }
    #     return validated
class PdfSerializer(serializers.ModelSerializer):
    class Meta:
        model=Conveyance
        fields='__all__'
class AnalyzedSerializer(serializers.ModelSerializer):
    conveyance = PdfSerializer()  
    class Meta:
        model=AnalyzedConveyance
        fields='__all__'

