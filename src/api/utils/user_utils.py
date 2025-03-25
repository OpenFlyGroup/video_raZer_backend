from os import path, remove
from random import choices
from string import ascii_letters, digits, punctuation

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from PIL import Image

from ..models import User


def validate_avatar(file: UploadedFile) -> None:
    if file.size > 5 * 1024 * 1024:
        raise ValidationError(message="Размер файла не должен превышать 5MB")
    valid_extensions = [".jpg", ".jpeg", ".png"]
    ext = path.splitext(p=file.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(message="Поддерживаются только файлы .jpg, .jpeg и .png")
    try:
        img = Image.open(fp=file)
        img.verify()
    except Exception:
        raise ValidationError(
            message="Файл поврежден или не является изображением"
        ) from ValidationError


def handle_avatar_upload(user: User, avatar_file: UploadedFile) -> str:
    if user.avatar:
        if path.isfile(path=user.avatar.path):
            remove(path=user.avatar.path)
    user.avatar = avatar_file
    user.save()
    if user.avatar:
        img_path = user.avatar.path
        img = Image.open(fp=img_path)
        if img.mode != "RGB":
            img = img.convert(mode="RGB")
        if img.height > 500 or img.width > 500:
            output_size = (500, 500)
            img.thumbnail(size=output_size)
        img.save(fp=img_path, quality=85, optimize=True)
    return user.avatar.url if user.avatar else None


def generate_password(length: int = 15) -> str:
    unsafe_characters = {'"', "'", "\\", "`"}
    safe_characters = "".join(
        ch
        for ch in (ascii_letters + digits + punctuation)
        if ch not in unsafe_characters
    )
    return "".join(choices(population=safe_characters, k=length))


def user_info(user: User) -> dict:
    info = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "isActive": user.is_active,
        "avatarPath": user.avatar.url if user.avatar else None,
    }
    return info
