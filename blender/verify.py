"""Validate decoded frames, rather than trusting container metadata alone."""
import argparse
import json
import subprocess
from fractions import Fraction
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('directory')
a = p.parse_args()
d = Path(a.directory)
m = json.loads((d / 'manifest.json').read_text())
result = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-show_streams',
    '-show_format', '-of', 'json', str(d / 'video.mp4')], check=True, capture_output=True, text=True)
(d / 'ffprobe.json').write_text(result.stdout)
data = json.loads(result.stdout)
v = [x for x in data['streams'] if x['codec_type'] == 'video']
assert len(v) == 1, v
v = v[0]
assert v['codec_name'] == 'h264' and v['pix_fmt'] == 'yuv420p', v
assert (v['width'], v['height']) == (m['width'], m['height']), v
assert Fraction(v['avg_frame_rate']) == m['fps'], v
assert int(v['nb_read_frames']) == m['frames'] > 0, v
assert abs(float(data['format']['duration']) - m['seconds']) <= 1 / m['fps'], data
subprocess.run(['ffmpeg', '-v', 'error', '-i', str(d / 'video.mp4'), '-f', 'null', '-'], check=True)
(d / 'verified.json').write_text(json.dumps({'valid': True, 'frames': m['frames'],
    'fps': m['fps'], 'duration': data['format']['duration'], 'width': v['width'], 'height': v['height']}, indent=2))
print((d / 'verified.json').read_text())
