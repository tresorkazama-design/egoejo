"""
Sérialiseurs pour les scrutins.
"""

from rest_framework import serializers

from core.models import Poll, PollBallot, PollOption

from .accounts import UserSummarySerializer


class PollOptionSerializer(serializers.ModelSerializer):
    votes = serializers.SerializerMethodField()

    class Meta:
        model = PollOption
        fields = ("id", "label", "position", "votes")

    def get_votes(self, obj):
        return obj.ballots.count()


class PollSerializer(serializers.ModelSerializer):
    options = PollOptionSerializer(many=True, read_only=True)
    created_by = UserSummarySerializer(read_only=True)
    total_votes = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = (
            "id",
            "title",
            "question",
            "description",
            "status",
            "is_anonymous",
            "allow_multiple",
            "quorum",
            "opens_at",
            "closes_at",
            "project",
            "created_by",
            "created_at",
            "updated_at",
            "options",
            "total_votes",
        )
        read_only_fields = ("created_by", "created_at", "updated_at", "total_votes")

    def get_total_votes(self, obj):
        return obj.ballots.count()


class PollVoteSerializer(serializers.Serializer):
    options = serializers.ListField(
        child=serializers.IntegerField(), min_length=1, allow_empty=False
    )

    def validate(self, attrs):
        poll = self.context["poll"]
        option_ids = attrs["options"]
        if len(option_ids) != len(set(option_ids)):
            raise serializers.ValidationError("Options dupliquees non autorisees.")
        qs = poll.options.filter(id__in=option_ids)
        if qs.count() != len(option_ids):
            raise serializers.ValidationError("Option invalide pour ce vote.")
        if not poll.allow_multiple and len(option_ids) > 1:
            raise serializers.ValidationError("Ce scrutin n'autorise qu'un seul choix.")
        return attrs


class PollBallotSerializer(serializers.ModelSerializer):
    option = PollOptionSerializer(read_only=True)

    class Meta:
        model = PollBallot
        fields = ("id", "poll", "option", "voter_hash", "metadata", "submitted_at")
        read_only_fields = ("voter_hash", "metadata", "submitted_at")

