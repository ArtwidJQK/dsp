with open('main/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

ids = [
    'scene-cover', 'scene-tuner', 'scene-info', 'curtainWrapper', 'app-stage',
    'btnMusic', 'btnSettings', 'btnStartTuner', 'btnBackToTuner',
    'navCover', 'navTuner', 'navInfo',
    'uiNote', 'uiFrequency', 'uiCentsMarker', 'uiCentsText',
    'uiTarget', 'uiConfidence', 'uiEstimator', 'uiStatusDot', 'uiStatusText'
]

missing = [i for i in ids if f'id="{i}"' not in content]
print('Missing IDs:', missing)
print('Has fetchRealtimeDSP:', 'fetchRealtimeDSP' in content)
print('Has /api/data:', '/api/data' in content)
print('Has applyMockDataToUI:', 'applyMockDataToUI' in content)
