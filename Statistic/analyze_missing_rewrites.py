import json

# Load original and rewritten data
with open('english_articles_june_july.json', encoding='utf-8') as f:
    orig = json.load(f)
with open('rewritten_thread.json', encoding='utf-8') as f:
    rew = json.load(f)

missing = [k for k in orig if '-' + str(k) not in rew]
print(f"Missing: {len(missing)} reports")

empty_desc_and_caption = 0
examples = []

for k in missing:
    hi = orig[k].get('Historical_Information', {})
    descs = hi.get('Description', [])
    images = hi.get('Image', [])
    all_desc_empty = all(('Description' in d and d['Description'].strip() == '') for d in descs) if descs else True
    all_caption_empty = all(('Caption' in img and img['Caption'].strip() == '') for img in images) if images else True
    if all_desc_empty and all_caption_empty:
        empty_desc_and_caption += 1
        if len(examples) < 5:
            examples.append(k)

print(f"Reports with all descriptions and image captions empty: {empty_desc_and_caption}")
if examples:
    print("Example keys:", examples) 