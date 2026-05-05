import json
from typing import Any, List, Dict
from sentence_transformers import SentenceTransformer, util
import openai
import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import datetime

model = SentenceTransformer('all-MiniLM-L6-v2')
api_key = os.getenv("OPENAI_API_KEY")

from transformers import T5Tokenizer, T5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained("Vamsi/T5_Paraphrase_Paws")
paraphrase_model = T5ForConditionalGeneration.from_pretrained("Vamsi/T5_Paraphrase_Paws")


def paraphrase(text: str) -> str:
    input_text = f"paraphrase: {text} </s>"
    encoding = tokenizer.encode_plus(input_text, return_tensors="pt", padding=True)
    outputs = model.generate(
        **encoding,
        max_length=256,
        num_return_sequences=1,
        num_beams=5,
        early_stopping=True
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def extract_text_with_path(data: Any, path: str = '') -> List[Dict[str, str]]:
    results = []

    if isinstance(data, dict):
        if 'Speaker' in data and 'Text' in data:
            combined_text = f"{data['Speaker']}: {data['Text']}"
            results.append({"path": path, "text": combined_text})
        elif 'Description' in data and isinstance(data['Description'], str):
            results.append({"path": path, "text": data['Description']})
        else:
            for key, value in data.items():
                if key == "Image":
                    continue
                new_path = f"{path}->{key}" if path else key
                results += extract_text_with_path(value, new_path)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            new_path = f"{path}[{i}]"
            results += extract_text_with_path(item, new_path)
    elif isinstance(data, str):
        results.append({"path": path, "text": data})

    return results


def preprocess_reports(data, max_count=100):
    processed = {}
    current_key = 0
    for i, (key, report) in enumerate(data.items()):
        # if i >= max_count:
        #     break

        # 過濾掉 Report_info 的文字內容
        text_nodes = [item for item in extract_text_with_path(report) if not item["path"].startswith("Report_info")]
        text_list = [item["text"] for item in text_nodes]
        # print(text_list)

        if not text_list:
            continue
        
        report_info = report.get("Report_info", [{}])[0]

        for text in text_list:
            embedding = model.encode(text, convert_to_tensor=True).unsqueeze(0)  # 保留 2D 結構

        # 儲存預處理後的內容
            processed[current_key] = {
                "embedding": embedding,
                "text_sample": text if text_list else "",
                "date": (
                    report_info.get("Year", ""),
                    report_info.get("Month", ""),
                    report_info.get("Day", "")
                )
            }
            current_key += 1
    return processed

def look_for_data(data):
    output_data = {}
    for key, report in data.items():
        # Only process if 'Historical_Information' and its 'Description' exist
        historical = report.get('Historical_Information', {})
        if not historical or 'Description' not in historical:
            continue
        descriptions = historical['Description']
        rewritten = False
        new_descriptions = []
        for desc in descriptions:
            orig_text = desc.get('Description', '')
            if not orig_text:
                new_descriptions.append(desc)
                continue
            # Paraphrase the description
            rewrite_text = paraphrase_with_gpt(orig_text)
            if rewrite_text and rewrite_text != orig_text:
                rewritten = True
                new_desc = desc.copy()
                new_desc['Description'] = rewrite_text
                new_descriptions.append(new_desc)
            else:
                new_descriptions.append(desc)
        if rewritten:
            # Create a new structure with only Report_info and rewritten Historical_Information
            new_report = {}
            if 'Report_info' in report:
                # Deep copy and minus one day on date
                orig_info = report['Report_info']
                new_info = []
                for info in orig_info:
                    info_copy = info.copy()
                    year = int(info_copy.get('Year', '1900'))
                    month = int(info_copy.get('Month', '1'))
                    day = int(info_copy.get('Day', '1'))
                    try:
                        date_obj = datetime.date(year, month, day) - datetime.timedelta(days=1)
                        info_copy['Year'] = str(date_obj.year)
                        info_copy['Month'] = f"{date_obj.month:02d}"
                        info_copy['Day'] = f"{date_obj.day:02d}"
                    except Exception as e:
                        print(f"Date error for key {key}: {e}")
                    new_info.append(info_copy)
                new_report['Report_info'] = new_info
            new_historical = {}
            # Rewrite Description
            new_historical['Description'] = new_descriptions
            # Rewrite Image captions
            if 'Image' in historical:
                new_images = []
                for image in historical['Image']:
                    new_image = dict(image)
                    if 'Caption' in new_image and new_image['Caption']:
                        new_image['Caption'] = paraphrase_with_gpt(new_image['Caption'])
                    new_images.append(new_image)
                new_historical['Image'] = new_images
            # Copy Speaker as-is if present
            if 'Speaker' in historical:
                new_historical['Speaker'] = historical['Speaker']
            new_report['Historical_Information'] = new_historical
            output_data[str(-int(key))] = new_report
    with open("rewritten_historical_info.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"\nTotal rewritten historical information entries: {len(output_data)}")

def paraphrase_with_gpt(text: str) -> str:
    client = openai.OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Please rewrite the input sentence to have the same meaning but a different syntax."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"GPT paraphrasing failed: {e}")
        return paraphrase(text)  # fallback

    
if __name__ == "__main__":
    json_path = "english_articles_june_july.json"
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    look_for_data(data)
