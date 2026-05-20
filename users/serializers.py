from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {'password': "Passwords do not match"}
            )
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        role = self.context.get('role', User.Role.CLIENT)
        validated_data['role'] = role
        return User.objects.create_user(**validated_data)
    
    