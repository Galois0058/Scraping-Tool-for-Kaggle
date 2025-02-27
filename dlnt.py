from kaggle import KaggleApi
import os
import re

def extract_dataset_name(url):
    """
    Extracts the dataset name from a Kaggle dataset URL with enhanced validation
    """
    pattern = r'https://www\.kaggle\.com/datasets/([^/]+)/([^/]+)(?:/.*)?$'
    match = re.match(pattern, url)
    if match:
        return f"{match.group(1)}/{match.group(2)}"
    else:
        raise ValueError(f"无效的数据集 URL: {url}")

def download_top_kernels(dataset_title, dataset_url):
    """
    Downloads the top 3 kernels for a given dataset with improved error handling
    """
    BASE_DIR = "./" 
    dataset_dir = os.path.join(BASE_DIR, dataset_title)
    
    try:
        dataset_name_kaggle = extract_dataset_name(dataset_url)
    except ValueError as e:
        print(f"URL解析失败: {e}")
        return

    # Authenticate with Kaggle API
    api = KaggleApi()
    try:
        api.authenticate()
    except Exception as e:
        print(f"Kaggle认证失败: {e}")
        return

    try:
        kernels = api.kernels_list(dataset=dataset_name_kaggle, sort_by='voteCount', page_size=3)
    except Exception as e:
        print(f"获取内核列表失败: {e}")
        return

    if not kernels:
        print(f"警告：数据集 {dataset_name_kaggle} 没有找到任何内核")
        return

    # Create the dataset directory
    os.makedirs(dataset_dir, exist_ok=True)
    
    for kernel in kernels:
        if not hasattr(kernel, 'ref'):
            print(f"跳过无效的内核: {getattr(kernel, 'title', '未知内核')}")
            continue

        kernel_ref = kernel.ref
        kernel_slug = kernel_ref.split('/')[-1]
        kernel_path = os.path.join(dataset_dir, kernel_slug)

        os.makedirs(kernel_path, exist_ok=True)

        # 下载代码
        try:
            api.kernels_pull(kernel=kernel_ref, path=kernel_path)
            print(f"✅ 代码下载成功: {kernel_slug}")
        except Exception as e:
            print(f"❌ 代码下载失败 [{kernel_slug}]: {str(e)}")

        # 下载输出
        try:
            api.kernels_output(kernel=kernel_ref, path=kernel_path)
            print(f"✅ 输出下载成功: {kernel_slug}")
        except Exception as e:
            print(f"❌ 输出下载失败 [{kernel_slug}]: {str(e)}")

def main():
    dataset_url = "https://www.kaggle.com/datasets/meharshanali/nvidia-stocks-data-2025"  
    dataset_name = "nvidia_stocks_data"
    download_top_kernels(dataset_name, dataset_url)

if __name__ == "__main__":
    main()