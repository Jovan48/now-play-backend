from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
        password = serializers.CharField(write_only=True, min_length=8)
        password2 = serializers.CharField(write_only=True, min_length=8, required=False)
        full_name = serializers.CharField(required=False, allow_blank=True, default='')
        stage_name = serializers.CharField(required=False, allow_blank=True, default='')
  
        class Meta:
            model = User
            fields = ['email', 'full_name', 'stage_name', 'password', 'password2']
  
        def validate_email(self, value):
            if User.objects.filter(email__iexact=value).exists():
                raise serializers.ValidationError('A user with that email already exists.')
            return value
  
        def validate(self, attrs):
            # Only check password2 matching if frontend provided it
            password2 = attrs.get('password2')
            if password2 and attrs['password'] != password2:
                raise serializers.ValidationError({'password2': 'Password fields did not match.'})
            
            validate_password(attrs['password'])
            if not any(char.isdigit() for char in attrs['password']):
                raise serializers.ValidationError({'password': 'Password must contain at least one number.'})
            return attrs
  
        def create(self, validated_data):
            validated_data.pop('password2', None)
            password = validated_data.pop('password')
            return User.objects.create_user(password=password, **validated_data)


class EmailVerificationSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_new_password(self, value):
        validate_password(value)
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError('Password must contain at least one number.')
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'full_name', 'stage_name', 'bio', 'genres', 'profile_photo', 'city', 'country']
        read_only_fields = ['email']
