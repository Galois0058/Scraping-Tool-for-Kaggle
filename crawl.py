import os
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
from kaggle.api.kaggle_api_extended import KaggleApi
from dlnt import download_top_kernels
import shutil 




def download_and_process_dataset(dataset_title, dataset_ref):
    api = KaggleApi()
    api.authenticate()  
    BASE_DIR = "./"

    dataset_dir = os.path.join(BASE_DIR, dataset_title)
    os.makedirs(dataset_dir, exist_ok=True)
    temp_dir = os.path.join(dataset_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    print(f"正在下载 {dataset_ref}...")
    api.dataset_download_files(dataset_ref, path=temp_dir, unzip=True)
    
    overall_size = 0
    train_size = 0
    test_size = 0
    is_splited = False
    cat_features = {}
    num_features = {}
    data_intro = None
    target_intro = None
    c_classes = 0
    n_classes = 0
    
    # 处理下载的文件
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            file_path = os.path.join(root, file)
            csv_file_path = os.path.join(root, f"{os.path.splitext(file)[0]}.csv")
            
            # 文件格式处理
            if file.endswith(".csv"):
                df = pd.read_csv(file_path)
            elif file.endswith(".json"):
                try:
                    df = pd.read_json(file_path)  
                    df.to_csv(csv_file_path, index=False)
                    print(f"已将 {file} 转换为 {os.path.basename(csv_file_path)}")  
                    df = pd.read_csv(csv_file_path)
                except Exception as e:
                    print(f"转换 {file} 到 CSV 时出错: {e}")
                    continue
            else:
                print(f"跳过不支持的文件格式: {file}")
                continue
            
            # 数据统计
            overall_size += len(df)
            
            # 特征类型判断
            for column in df.columns:
                if pd.api.types.is_numeric_dtype(df[column]):
                    n_classes += 1
                    num_features[column] = {}
                else:
                    c_classes += 1
                    cat_features[column] = {}
            # 数据集分割（将文件移动到 dataset_dir 根目录）
            output_file_name = os.path.basename(file_path) 
            if "train" in file.lower():
                train_size = len(df)
                df.to_csv(os.path.join(dataset_dir, "train.csv"), index=False)
                is_splited = True
            elif "test" in file.lower():
                test_size = len(df)
                df.to_csv(os.path.join(dataset_dir, "test.csv"), index=False)
                is_splited = True
            else:
                df.to_csv(os.path.join(dataset_dir, output_file_name), index=False)

    try:
        shutil.rmtree(temp_dir)
        print(f"成功清理临时目录: {temp_dir}")
    except Exception as e:
        print(f"清理临时目录时出错: {str(e)}")

    keys_union = set(cat_features.keys()).union(set(num_features.keys()))
    dataset_url = f"https://www.kaggle.com/datasets/{dataset_ref}/data"
    try:
        response = requests.get(dataset_url, timeout=10)
        if response.status_code == 200: 
            soup = BeautifulSoup(response.text, "html.parser")
            script_tag = soup.find('script', {'type': 'application/ld+json'})
            if script_tag:
                try:
                    json_data = json.loads(script_tag.string)
                    description = json_data.get('description', '')
                    print(f"数据集描述: {description}")
                    data_intro = None
                    for line in description.split('\n'):
                        line = line.strip()
                        if line.lower().startswith('the')or line.lower().startswith('this'): 
                            data_intro = line
                            break
                    for line in description.split('\n'):
                        line = line.strip()
                        if 'idea' in line.lower() or'goal' in line.lower():
                            target_intro=line
                    for line in description.split('\n'):
                        line = line.strip()
                        for string in keys_union:
                                if string.lower() in line.lower():
                                    if string in cat_features:
                                        cat_features[string] = line
                                    if string in num_features:
                                        num_features[string] = line
                except json.JSONDecodeError:
                    print("JSON 解析失败")
            else:
                print("未找到描述信息的 JSON 数据")
        else:
            print(f"请求 {dataset_url} 失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"获取数据集描述时出错: {e}")

    # 保存信息到 info.json
    info = {
        "name": dataset_title,
        "source": dataset_url,
        "data_intro": data_intro ,
        "target_intro": target_intro,
        "is_splited": is_splited,
        "overall_size": overall_size,
        "train_size": train_size,
        "test_size": test_size,
        "c_classes": c_classes,
        "n_classes": n_classes,
        "cat_feature_intro": cat_features,
        "num_feature_intro": num_features
    }

    with open(os.path.join(dataset_dir, "info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4, ensure_ascii=False)
    print(f"已处理 {dataset_ref} 到 {dataset_dir}")

