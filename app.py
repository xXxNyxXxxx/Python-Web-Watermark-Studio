import os
import zipfile
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
WATERMARKED_FOLDER = 'static/watermarked'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(WATERMARKED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['WATERMARKED_FOLDER'] = WATERMARKED_FOLDER


def get_font(font_style, size_choice, height):
    """Selects font typeface and scales size proportionally to image height."""
    scale_factors = {'small': 0.02, 'medium': 0.04, 'large': 0.07}
    factor = scale_factors.get(size_choice, 0.04)
    font_size = max(int(height * factor), 14)

    # Map UI font choices to common cross-platform system fonts
    font_map = {
        'sans-serif': ["arial.ttf", "DejaVuSans.ttf", "Helvetica.ttf"],
        'serif': ["times.ttf", "DejaVuSerif.ttf", "Georgia.ttf"],
        'monospace': ["cour.ttf", "DejaVuSansMono.ttf", "Consolas.ttf"]
    }

    candidates = font_map.get(font_style, font_map['sans-serif'])
    for font_name in candidates:
        try:
            return ImageFont.truetype(font_name, font_size)
        except IOError:
            continue
    return ImageFont.load_default()


def apply_watermark(input_path, output_path, watermark_text, logo_path, watermark_type, position, size_choice, font_style, opacity, rotation_angle):
    """Core Pillow engine: handles either an image logo or text watermark with custom positioning, opacity & rotation."""
    img = Image.open(input_path).convert("RGBA")
    width, height = img.size
    
    # Create an overlay layer for the watermark
    txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    padding = int(width * 0.03)

    # --- BRANCH A: LOGO WATERMARK ---
    if watermark_type == 'logo' and logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        
        scale_ratios = {'small': 0.10, 'medium': 0.20, 'large': 0.35}
        target_logo_width = int(width * scale_ratios.get(size_choice, 0.20))
        
        logo_w, logo_h = logo.size
        aspect_ratio = logo_h / logo_w
        target_logo_height = int(target_logo_width * aspect_ratio)
        logo = logo.resize((target_logo_width, target_logo_height), Image.Resampling.LANCZOS)
        
        if opacity < 255:
            bands = logo.split()
            if len(bands) == 4:
                r, g, b, alpha = bands
                alpha = Image.eval(alpha, lambda a: int(a * (opacity / 255.0)))
                logo = Image.merge("RGBA", (r, g, b, alpha))
            
        l_w, l_h = logo.size
        
        positions_map = {
            'top-left': (padding, padding),
            'top-right': (width - l_w - padding, padding),
            'mid-left': (padding, (height // 2) - (l_h // 2)),
            'mid-right': (width - l_w - padding, (height // 2) - (l_h // 2)),
            'bottom-left': (padding, height - l_h - padding),
            'bottom-right': (width - l_w - padding, height - l_h - padding)
        }
        
        if position == 'grid':
            # Rotate the logo using the dynamic user-defined angle
            rotated_logo = logo.rotate(rotation_angle, expand=True)
            r_w, r_h = rotated_logo.size
            
            step_x = r_w + int(width * 0.15)
            step_y = r_h + int(height * 0.15)
            for y in range(-r_h, height + r_h, step_y):
                for x in range(-r_w, width + r_w, step_x):
                    txt_layer.paste(rotated_logo, (x, y), rotated_logo)
        else:
            coords = positions_map.get(position, positions_map['bottom-right'])
            txt_layer.paste(logo, coords, logo)

    # --- BRANCH B: TEXT WATERMARK ---
    else:
        draw = ImageDraw.Draw(txt_layer)
        font = get_font(font_style, size_choice, height)

        # Measure exact text dimensions
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        positions_map = {
            'top-left': (padding, padding),
            'top-right': (width - text_width - padding, padding),
            'mid-left': (padding, (height // 2) - (text_height // 2)),
            'mid-right': (width - text_width - padding, (height // 2) - (text_height // 2)),
            'bottom-left': (padding, height - text_height - padding),
            'bottom-right': (width - text_width - padding, height - text_height - padding)
        }

        if position == 'grid':
            box_width = text_width + 40
            box_height = text_height + 40
            single_txt_img = Image.new("RGBA", (box_width, box_height), (255, 255, 255, 0))
            single_draw = ImageDraw.Draw(single_txt_img)
            
            # Use user-defined opacity (slightly softened for the grid background pattern)
            grid_opacity = int(opacity * 0.7) 
            single_draw.text((20, 20), watermark_text, fill=(255, 255, 255, grid_opacity), font=font)

            # Rotate the text tile using the dynamic user-defined angle
            rotated_text_img = single_txt_img.rotate(rotation_angle, expand=True)
            r_w, r_h = rotated_text_img.size

            step_x = r_w + int(width * 0.12)
            step_y = r_h + int(height * 0.12)

            for y in range(-r_h, height + r_h, step_y):
                for x in range(-r_w, width + r_w, step_x):
                    txt_layer.paste(rotated_text_img, (x, y), rotated_text_img)
        else:
            coords = positions_map.get(position, positions_map['bottom-right'])
            # Apply exact user-defined opacity here
            draw.text(coords, watermark_text, fill=(255, 255, 255, opacity), font=font)

    watermarked = Image.alpha_composite(img, txt_layer)
    watermarked.convert("RGB").save(output_path, "JPEG", quality=95)


@app.route('/', methods=['GET', 'POST'])
def index():
    single_image = None
    batch_zip = None
    processed_files = []

    if request.method == 'POST':
        files = request.files.getlist('images')
        watermark_type = request.form.get('watermark_type', 'text')
        watermark_text = request.form.get('watermark_text', '© Portfolio')
        position = request.form.get('position', 'bottom-right')
        size_choice = request.form.get('size', 'medium')
        font_style = request.form.get('font_style', 'sans-serif')
        opacity = int(request.form.get('opacity', 160))
        rotation_angle = int(request.form.get('rotation', -30)) # Get rotation angle from form

        # Handle optional logo upload
        logo_file = request.files.get('logo_file')
        logo_path = None
        if logo_file and logo_file.filename != '':
            logo_filename = secure_filename(logo_file.filename)
            logo_path = os.path.join(app.config['UPLOAD_FOLDER'], logo_filename)
            logo_file.save(logo_path)

        # Filter out empty file submissions
        valid_files = [f for f in files if f and f.filename != '']

        if not valid_files:
            return redirect(request.url)

        for file in valid_files:
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)

            base_name = os.path.splitext(filename)[0]
            output_filename = f"watermarked_{base_name}.jpg"
            output_path = os.path.join(app.config['WATERMARKED_FOLDER'], output_filename)

            apply_watermark(input_path, output_path, watermark_text, logo_path, watermark_type, position, size_choice, font_style, opacity, rotation_angle)
            processed_files.append(output_filename)

        if len(processed_files) == 1:
            single_image = processed_files[0]
        elif len(processed_files) > 1:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f"watermarked_batch_{timestamp}.zip"
            zip_path = os.path.join(app.config['WATERMARKED_FOLDER'], zip_filename)

            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for fname in processed_files:
                    file_full_path = os.path.join(app.config['WATERMARKED_FOLDER'], fname)
                    zipf.write(file_full_path, arcname=fname)

            batch_zip = zip_filename

    return render_template(
        'index.html',
        single_image=single_image,
        batch_zip=batch_zip,
        processed_files=processed_files
    )


if __name__ == '__main__':
    app.run(debug=True)