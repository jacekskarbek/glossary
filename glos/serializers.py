from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Term, UserTermbase, Termbase, Language
from rest_framework.fields import CurrentUserDefault

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups','date_joined', 'last_login', 'is_superuser')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')
        
        

class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        #fields = ('value',)
        fields = ('id', 'entry', 'language', 'termbase', 'value', 'added', 'updated', 'creator')


class TermbaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Termbase
        fields = ('name',)

class UserTermbaseSerializer(serializers.ModelSerializer):
	#user=serializers.SlugRelatedField(read_only=True, slug_field='username')
	#termbase=serializers.SlugRelatedField(read_only=True, slug_field='termbase_name')
	#user=serializers.PrimaryKeyRelatedField(read_only=True)
	#user = serializers.RelatedField(read_only=True)
	#user=UserSerializer()
	termbase=serializers.ReadOnlyField()
	user=serializers.ReadOnlyField()
	#user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())   # expected pk value
	#print(user)
	#user = serializers.ReadOnlyField(source='user.username')
	class Meta:
		model = UserTermbase
		fields = ('user','write', 'read','termbase', )
		
	def validate_user(self, user):
		print(user)
		try:
			data = User.objects.get(username=user)
		except Exception as e:
			raise serializers.ValidationError("Wrong User")
		return data
	def validate_termbase(self, termbase):
		try:
			data = Termbase.objects.get(name=termbase)
		except Exception as e:
			raise serializers.ValidationError("Wrong Termbase")
		return data
	
class UserTermbaseSerial(serializers.Serializer):
	read = serializers.BooleanField()
	write = serializers.BooleanField()
	user = serializers.CharField()
	termbase=serializers.CharField()
	def create(self, validated_data):
		album = UserTermbase.objects.create(**validated_data)
		return album
	def validate_user(self, user):
		try:
			data = User.objects.get(username=user)
		except Exception as e:
			raise serializers.ValidationError("Wrong User")
		return data
	def validate_termbase(self, termbase):
		try:
			data = Termbase.objects.get(name=termbase)
		except Exception as e:
			raise serializers.ValidationError("Wrong Termbase")
		return data
	
class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ('name',)
        
class DescriptionSerializer(serializers.Serializer):
	value = serializers.CharField()
	type = serializers.CharField()
	name = serializers.CharField()
	
class TermGrpSerializer(serializers.Serializer):
	value = serializers.CharField()
	descripGrp = DescriptionSerializer(many=True)
	
class LangSerializer(serializers.Serializer):
	lang = serializers.CharField()
	termGrp = TermGrpSerializer(many=True)
	descripGrp = DescriptionSerializer(many=True)
	
class ResultsSerializer(serializers.Serializer):
	id = serializers.CharField()
	languages = LangSerializer(many=True)
	descripGrp = DescriptionSerializer(many=True)
	term = serializers.CharField()
	#termbase = serializers.CharField()

class TermbaseResultsSerializer(serializers.Serializer):
	entries = ResultsSerializer(many=True)
	name = serializers.CharField()