from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(label="Username", write_only=True)
    password = serializers.CharField(
        label="Password",
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"), username=username, password=password
        )
        if not user:
            msg = "Wrong username or password."
            raise serializers.ValidationError(msg, code="authorization")
        attrs["user"] = user
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        user_model = get_user_model()
        try:
            user_model.objects.get(email=data["email"])
        except user_model.DoesNotExist:
            return data
        else:
            raise serializers.ValidationError(
                {"email": "An account with this email address already exists."}
            )

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = get_user_model()(**validated_data)
        user.set_password(validated_data["password"])
        user.save()

        return user


class ProfileSerializer(serializers.ModelSerializer):
    date_joined = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "date_joined"]

    def get_date_joined(self, obj):
        return obj.date_joined.date()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, data):
        new_password = data.get("new_password")

        # Assign validation errors to "new_password" field
        errors = dict()
        try:
            validate_password(password=new_password)
        except ValidationError as e:
            errors["new_password"] = list(e.messages)
        if errors:
            raise serializers.ValidationError(errors)
        return super(ChangePasswordSerializer, self).validate(data)
