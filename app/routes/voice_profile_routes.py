from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.controllers import voice_profile_controller as ctrl

voice_profile_bp = Blueprint("voice_profile", __name__, url_prefix="/api/voice-profiles")


@voice_profile_bp.route("", methods=["POST"])
@jwt_required()
def create_voice_profile():
    return ctrl.create_voice_profile()


@voice_profile_bp.route("", methods=["GET"])
@jwt_required()
def list_voice_profiles():
    return ctrl.list_voice_profiles()


@voice_profile_bp.route("/<int:voice_profile_id>/status", methods=["GET"])
@jwt_required()
def get_voice_profile_status(voice_profile_id):
    return ctrl.get_voice_profile_status(voice_profile_id)


@voice_profile_bp.route("/<int:voice_profile_id>", methods=["DELETE"])
@jwt_required()
def delete_voice_profile(voice_profile_id):
    return ctrl.delete_voice_profile(voice_profile_id)
