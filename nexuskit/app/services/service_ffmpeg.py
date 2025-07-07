import os
import ffmpeg
from . import cleanup_service, task_service

def handle_ffmpeg_upload(file):
    task_id = task_service.create_task(tool_name='ffmpeg')
    task_dir = os.path.join(cleanup_service.TEMP_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)

    original_file_path = os.path.join(task_dir, file.filename)
    with open(original_file_path, "wb") as buffer:
        buffer.write(file.file.read())

    task_service.update_task_progress(task_id, 0) # Mark as uploaded
    cleanup_service.schedule_cleanup(task_id)

    return {"task_id": task_id, "filename": file.filename, "original_file_path": original_file_path}

def run_ffmpeg_conversion(task_id: str, original_file_path: str, output_format: str, extract_audio: bool, resolution: str | None, quality: str | None, bitrate: str | None):
    task_dir = os.path.dirname(original_file_path)
    output_filename = f"{os.path.splitext(os.path.basename(original_file_path))[0]}.{output_format}"
    output_file_path = os.path.join(task_dir, output_filename)

    try:
        task_service.update_task_progress(task_id, 10) # Mark as starting
        input_stream = ffmpeg.input(original_file_path)
        output_stream = None

        if extract_audio:
            output_stream = input_stream.audio.output(output_file_path, acodec=output_format)
        else:
            video = input_stream.video
            audio = input_stream.audio
            if resolution:
                video = video.filter('scale', -1, resolution)
            
            kwargs = {}
            if quality:
                if quality == "High":
                    kwargs['crf'] = 18
                elif quality == "Medium":
                    kwargs['crf'] = 23
                elif quality == "Low":
                    kwargs['crf'] = 28
            if bitrate:
                kwargs['audio_bitrate'] = bitrate

            output_stream = ffmpeg.output(video, audio, output_file_path, **kwargs)

        task_service.update_task_progress(task_id, 50) # Mark as processing
        output_stream.run(overwrite_output=True)
        task_service.complete_task(task_id, output_file_path)

    except ffmpeg.Error as e:
        task_service.fail_task(task_id, e.stderr.decode('utf8'))
    except Exception as e:
        task_service.fail_task(task_id, str(e))
