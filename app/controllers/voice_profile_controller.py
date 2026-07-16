from flask import jsonify, request
from flask_jwt_extended import current_user

from app.extensions import db
from app.models.voice_profile_model import VoiceProfile, STATUS_PROCESSING
from app.middleware import voice_profile_belongs_to_current_parent


def create_voice_profile():
    """Uploads a voice recording and kicks off AI voice-model training.

    NOTE: actual voice cloning/training is expected to run in an async worker
    (e.g. Celery/RQ) that flips `status` to "ready" or "failed" once done. This
    endpoint only registers the sample and enqueues that work.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body is required."}), 400

    voice_sample_url = data.get("voice_sample_url")
    if not voice_sample_url or str(voice_sample_url).strip() == "":
        errors = ["voice_sample_url is required."]
        return jsonify({"errors": errors}), 400

    try:
        voice_profile = VoiceProfile(
            parent_id=current_user.id,
            label=str(data.get("label")).strip() if data.get("label") else None,
            voice_sample_url=str(voice_sample_url).strip(),
            status=STATUS_PROCESSING,
        )
        db.session.add(voice_profile)
        db.session.commit()

        # TODO: enqueue_voice_training_job(voice_profile.id)

        return jsonify(
            {
                "message": "Voice sample received. Training has started.",
                "voice_profile": voice_profile.to_dict(),
            }
        ), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500


def list_voice_profiles():
    profiles = VoiceProfile.query.filter_by(parent_id=current_user.id).order_by(
        VoiceProfile.id.desc()
    ).all()
    return jsonify({"voice_profiles": [p.to_dict() for p in profiles]}), 200


def get_voice_profile_status(voice_profile_id):
    profile = db.session.get(VoiceProfile, voice_profile_id)
    if not voice_profile_belongs_to_current_parent(profile):
        return jsonify({"error": "Voice profile not found."}), 404

    return jsonify({"id": profile.id, "status": profile.status}), 200


def delete_voice_profile(voice_profile_id):
    profile = db.session.get(VoiceProfile, voice_profile_id)
    if not voice_profile_belongs_to_current_parent(profile):
        return jsonify({"error": "Voice profile not found."}), 404

    try:
        db.session.delete(profile)
        db.session.commit()
        return jsonify({"message": "Voice profile and recording deleted successfully."}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500
