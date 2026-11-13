def _mean(buf):
    return sum(buf) / len(buf)
 
def _find_valleys(buf, min_distance=10, threshold_ratio=0.6):
    if not buf:
        return []
    threshold = min(buf) + (max(buf) - min(buf)) * (1 - threshold_ratio)
    valleys    = []
    last_valley = -min_distance
    for i in range(1, len(buf) - 1):
        if buf[i] < buf[i-1] and buf[i] < buf[i+1] and buf[i] < threshold:
            if i - last_valley >= min_distance:
                valleys.append(i)
                last_valley = i
    return valleys

def _downsample(buf, factor):
    result = []
    for i in range(0, len(buf) - factor, factor):
        result.append(_mean(buf[i:i + factor]))
    return result     

def calculate_heart_rate(ir_buf, sample_rate=25):
    ir = ir_buf[20:] if len(ir_buf) > 20 else ir_buf
    valleys = _find_valleys(ir)
 
    if len(valleys) < 2:
        return None
 
    intervals = [valleys[i+1] - valleys[i] for i in range(len(valleys) - 1)]
    avg_interval = _mean(intervals)

    bpm = 60.0 / (avg_interval / sample_rate)
 
    if 40 <= bpm <= 200:
        return round(bpm, 1)
    return None

def calculate_spo2(red_buf, ir_buf):
    red = red_buf[20:] if len(red_buf) > 20 else red_buf
    ir  = ir_buf[20:]  if len(ir_buf)  > 20 else ir_buf
    if len(red_buf) < 10 or len(ir_buf) < 10:
        return None
    ac_red = max(red_buf) - min(red)
    ac_ir  = max(ir_buf)  - min(ir)
    dc_red = _mean(red)
    dc_ir  = _mean(ir)
    if dc_red == 0 or dc_ir == 0 or ac_ir == 0:
        return None
    R = (ac_red / dc_red) / (ac_ir / dc_ir)
    spo2 = 104.0 - 17.0 * R
    if 70 <= spo2 <= 100:
        return round(spo2, 1)
    return None


def calculate_respiratory_rate(ir_buf, sample_rate=25):
    if len(ir_buf) < 200:
        return None
    
    ir = ir_buf[20:]

    slow_signal = _downsample(ir, factor=10)

    if len(slow_signal) < 4:
        return None
    
    breath_valleys = _find_valleys(slow_signal, min_distance=15, threshold_ratio=0.2)

    if len(breath_valleys) < 2:
        return None
    
    intervals = [breath_valleys[i+1] - breath_valleys[i] for i in range(len(breath_valleys) - 1)]
    avg_interval = _mean(intervals)

    downsample_rate = sample_rate / 10
    breaths_per_min = 60.0 / (avg_interval / downsample_rate)

    if 8 <= breaths_per_min <= 40:
        return round(breaths_per_min, 1)
    return None