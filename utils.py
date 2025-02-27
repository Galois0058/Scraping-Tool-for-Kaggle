import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi
from crawl import download_and_process_dataset
from dlnt import download_top_kernels


api = KaggleApi()
api.authenticate()  
# 通过Kaggle的api读取数据集列表
datasets = api.dataset_list(sort_by="votes", size=None, file_type="csv",page=10)[:10]                                                                                                        
dataref_list=[d.ref for d in datasets]
datatitle_list = [d.title for d in datasets]
print("数据集列表:", datatitle_list)
# 或手动输入ref列表和title列表
# dataset_ref=["meharshanali/nvidia_stocks_data_2025"]
# datapath=["./nvidia_stocks_data_2025"]

def main():
    for datatitle, data_ref in zip(datatitle_list, dataref_list):
        dataset_url = f"https://www.kaggle.com/datasets/{data_ref}"
        try:
            download_and_process_dataset(datatitle, data_ref)
        except Exception as e:
            print(f"处理 {datatitle} 时出错: {e}")
        try:
            download_top_kernels(datatitle, dataset_url)
        except Exception as e:
            print(f"下载{datatitle} 的笔记本时出错: {e}")

if __name__ == "__main__":
    main()