import json
import os
import glob

raw_files = glob.glob('*.json')

for file in raw_files:
    print(f'🔃 Dumping: {file}')
    
    try:
        with open(file, 'r') as f:
            json_data = json.load(f)
            if not json_data:
                continue

        with open(f"{file.split('.')[0]}.txt", 'w') as f:
            f.write(str(json_data))
        
        print(f'✅ Success: {file}')

    except Exception as e: 
        print(f'❌ Failed: {file}: {e}')

