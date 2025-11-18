import os
import subprocess
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Trigger
from PIL import Image, ImageDraw, ImageFont
import qrcode
from io import BytesIO

MINDAR_COMPILER_DIR = os.path.join(settings.BASE_DIR, 'mindar-compiler')
COMPILER_PATH = os.path.join(MINDAR_COMPILER_DIR, 'compiler.bundled.cjs')

@csrf_exempt
def upload_view(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        if not image or not video:
            return JsonResponse({'error': 'Select both image and video'}, status=400)

        # GET ORIGINAL FILENAME (without extension)
        original_name = os.path.splitext(image.name)[0]

        trigger = Trigger.objects.create(
            image=image,
            video=video,
            original_name=original_name
        )

        # Generate .mind
        if not generate_mind_file(trigger):
            trigger.delete()
            return JsonResponse({'error': 'Failed to generate AR target'}, status=500)

        return JsonResponse({
            'uid': str(trigger.uid),
            'image_url': trigger.image.url,
            'ar_url': f"/ar/{trigger.uid}/",
            'card_url': f"/card/{trigger.uid}/",
        })
    return render(request, 'upload.html')

def ar_scan(request, uid):
    trigger = get_object_or_404(Trigger, uid=uid)
    if not trigger.mind_file:
        return render(request, 'upload.html', {'error': 'Processing...'})
    return render(request, 'ar_scan.html', {'trigger': trigger})

def download_card(request, uid):
    trigger = get_object_or_404(Trigger, uid=uid)
    card = make_card(trigger)
    response = FileResponse(card, content_type='image/png')
    filename = f"{trigger.original_name}_card.png"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

def list_cards(request):
    triggers = Trigger.objects.all().order_by('-created_at')
    return render(request, 'list.html', {'triggers': triggers})

def make_card(trigger):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(f"{getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')}/ar/{trigger.uid}/")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    card_w, card_h = 1200, 1800
    card = Image.new("RGB", (card_w, card_h), "white")

    img = Image.open(trigger.image.path).convert("RGBA")
    max_w = int(card_w * 0.75)
    ratio = max_w / img.width
    new_h = int(img.height * ratio)
    img = img.resize((max_w, new_h), Image.LANCZOS)

    pos = ((card_w - img.width) // 2, 200)
    card.paste(img, pos, img)

    qr_pos = (card_w - qr_img.width - 100, card_h - qr_img.height - 100)
    card.paste(qr_img, qr_pos, qr_img)

    draw = ImageDraw.Draw(card)
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()
    draw.text((100, card_h - 200), "Scan → Video plays!", fill="black", font=font)

    buf = BytesIO()
    card.save(buf, format="PNG")
    buf.seek(0)
    return buf

def generate_mind_file(trigger):
    img_path = trigger.image.path
    mind_dir = os.path.join(settings.MEDIA_ROOT, 'minds')
    mind_filename = f"{trigger.original_name}.mind"
    mind_path = os.path.join(mind_dir, mind_filename)
    os.makedirs(mind_dir, exist_ok=True)

    cmd = ['node', COMPILER_PATH, '--input', img_path, '--output', mind_path]

    try:
        result = subprocess.run(
            cmd,
            cwd=MINDAR_COMPILER_DIR,
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
        print("MindAR Success:", result.stdout)
    except Exception as e:
        print("MindAR Failed:", str(e))
        return False

    # Save relative path
    rel_path = f"minds/{trigger.original_name}.mind"
    trigger.mind_file = rel_path
    trigger.save()
    return True

from django.http import StreamingHttpResponse
import time
import json

def progress_view(request):
    uid = request.GET.get('uid')
    if not uid:
        return JsonResponse({'error': 'No UID'}, status=400)

    def event_stream():
        progress = 0
        steps = [
            ("Reading image...", 10),
            ("Extracting features...", 40),
            ("Building target...", 70),
            ("Finalizing .mind file...", 95),
            ("Complete!", 100)
        ]

        for message, target in steps:
            # Simulate work
            while progress < target:
                progress += 5
                if progress > target:
                    progress = target
                yield f"data: {json.dumps({'progress': progress, 'message': message})}\n\n"
                time.sleep(0.1)  # Adjust speed

        yield f"data: {json.dumps({'progress': 100, 'done': True})}\n\n"

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')