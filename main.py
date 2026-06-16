import requests
import warnings
import pandas as pd

from datetime import datetime, timezone, timedelta

def fetch_dam_data() -> pd.DataFrame:
    """
    Fetch dam information from thai-water-api
    """
    try:
        url = 'https://api-v3.thaiwater.net/api/v1/thaiwater30/analyst/dam'
        response = requests.get(url, verify=False)
        data = response.json()
    except Exception as e:
        print(f"Failed to fetch API: {e}")
        raise

    targets = ['สิริกิติ์', 'ภูมิพล','อุบลรัตน์','ลำตะคอง','หนองปลาไหล']
    
    viewed = data['data']['dam_daily'].copy()
    df = pd.json_normalize(viewed)

    filtered = (
        df[df['dam.dam_name.th'].isin(targets) & (df['dam_storage_percent'] != 0)]
        [['dam.id','dam.dam_name.th', 'dam_storage_percent', 'dam_released']]
        .rename(columns={'dam.id': 'id', 'dam.dam_name.th': 'ชื่อ', 'dam_storage_percent': 'น้ำในอ่าง', 'dam_released':'ปริมาตรน้ำระบาย'})
        .set_index('id')
    )

    return filtered


def fetch_station_data() -> pd.DataFrame:
    """
    Fetch station information from thai-water-api
    """
    try:
        url = 'https://api-v3.thaiwater.net/api/v1/thaiwater30/public/waterlevel_load'
        response = requests.get(url, verify=False)
        data = response.json()
    except Exception as e:
        print(f"Failed to fetch API: {e}")
        raise

    targets = ['ที่ว่าการอ.นครชัยศรี',
                'บ้านม่วงก็อง','บ้านบางศาลา','บ้านคลองหวะ',
                'บ้านแม่แต','บ้านริมใต้','สะพานนวรัฐ',
                'ท่าขนอม','บ้านย่านดินแดง','บ้านเคียนซา','บ้านท่าข้าม',
                'บ้านท่านางเลื่อน','บ้านท่าเม่า',
                'ท้ายเขื่อนนเรศวร','สะพานสุพรรณกัลยา ',
                'บ้านเขื่องใน','สะพานเสรีประชาธิปไตย',
                'บ้านลาดบัวขาว','บ้านโคกกรวด','ตำบลในเมือง','บ้านโนนสะอาด',
                'บ้านค่าย','บ้านเขาโบสถ์'
                ]
    
    viewed = data['waterlevel_data']['data'].copy()
    df = pd.json_normalize(viewed)
    filtered = (
        df[df['station.tele_station_name.th'].isin(targets)]
        [['station.id','station.tele_station_name.th', 'discharge', 'waterlevel_msl']]
        .rename(columns={'station.id': 'id', 'station.tele_station_name.th': 'สถานี', 'discharge': 'ปริมาณน้ำท่า', 'waterlevel_msl': 'ระดับน้ำ'})
        .set_index('id')
    )

    return filtered


def fetch_reservoir_data() -> pd.DataFrame:
    """
    Fetch reservior information rid-api
    """
    try:
        url = 'https://app.rid.go.th/reservoir/api/reservoir/public'
        response = requests.get(url, verify=False)
        data = response.json()
    except Exception as e:
        print(f"Failed to fetch API: {e}")
        raise

    targets = ['อ่างเก็บน้ำคลองใหญ่','อ่างเก็บน้ำดอกกราย']
    
    viewed = data['data'].copy()
    df = pd.json_normalize(viewed)

    df_east = df[df['region']=='ภาคตะวันออก'].copy()
    df_east_detail = pd.DataFrame(df_east['reservoir'].tolist()[0])

    filtered = (
        df_east_detail[df_east_detail['name'].isin(targets)]
            [['id','name', 'percent_storage', 'outflow']]
            .rename(columns={'id': 'id', 'name': 'อ่างเก็บน้ำ', 'percent_storage': 'ปริมาณน้ำในอ่าง', 'outflow': 'น้ำระบาย'})
            .set_index('id')
    )

    return filtered


def fetch_rainfall_data() -> pd.DataFrame:
    """
    Fetch rainfall information from thai-water-api
    """
    try:
        url = 'https://api-v3.thaiwater.net/api/v1/thaiwater30/provinces/rain3d'
        response = requests.get(url, verify=False)
        data = response.json()
    except Exception as e:
        print(f"Failed to fetch API: {e}")
        raise

    targets = ['สะเดา','อบต.พิจิตร','พุนพิน 1','ขอนแก่น','ทต.ไชยมงคล']
    
    viewed = data['data'].copy()
    df = pd.json_normalize(viewed)

    filtered = (
        df[df['station.tele_station_name.th'].isin(targets)]
            [['station.id','station.tele_station_name.th','rain_3d']]
            .rename(columns={'station.id': 'id', 'station.tele_station_name.th': 'ชื่อสถานี', 'rain_3d': 'ฝนสะสม'})
            .set_index('id')
    )

    return filtered


def fetch_weather_forecast(filepath: str = "README.md"):
    """
    Fetch weather forecast information from tmd.go.th
    """
    url = "https://tmd.go.th/forecast/daily"

    response = requests.get(url, verify=False)
    response.encoding = "utf-8"

    tree = html.fromstring(response.content)
    xpath = "//div[contains(., 'ลักษณะอากาศทั่วไป')]//p"

    results = tree.xpath(xpath)

    if results:
        report = ""
        for i in range(len(results)):
            raw_text = results[i].text_content().strip()
            clean_text = html_lib.unescape(raw_text).replace('\xa0', ' ')
            if "ออกประกาศ" in clean_text:
                raw_text = results[i+1].text_content().strip()
                report = html_lib.unescape(raw_text).replace('\xa0', ' ')
                break

        with open(filepath, "a", encoding="utf-8") as f:
            f.write(report + "\n\n")
    
    else:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write("Unable to obtain the information\n\n")
        
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(f"Reference Link: {url}\n\n")

    print("Successfully write down a weather forecast")


def write_df_to_readme(df: pd.DataFrame, title: str = "", filepath: str = "README.md", mode: str = "w") -> None:
    """
    Convert a DataFrame to a Markdown table and write it to a .md file.

    Args:
        df      : DataFrame to convert.
        title   : Optional heading to place above the table.
        filepath: Path to the markdown file (default: README.md).
        mode    : 'w' to overwrite, 'a' to append.
    """
    md_table = df.to_markdown()

    with open(filepath, mode, encoding="utf-8") as f:
        if title:
            f.write(f"## {title}\n\n")
        f.write(md_table + "\n\n")

    print(f"Successfully write down a table {title}")


if __name__ == "__main__":
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')

    ict = timezone(timedelta(hours=7))
    timestamp = datetime.now(ict)
 
    # Update title
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(f"# Thai Water Report\n\nวันที่อัพเดทล่าสุด: {timestamp.year}-{timestamp.month}-{timestamp.day}\n\n")

    # Weather Forecast
    fetch_weather_forecast()

    # Dam
    dam_data = fetch_dam_data()
    write_df_to_readme(dam_data, title="ข้อมูลเขื่อน", mode="a")

    # Station
    station_data = fetch_station_data()
    write_df_to_readme(station_data, title="ระดับน้ำ", mode="a")

    # Reservoir
    reservoir_data = fetch_reservoir_data()
    write_df_to_readme(reservoir_data, title="อ่างเก็บน้ำ", mode="a")

    # Rainfall
    rainfall_data = fetch_rainfall_data()
    write_df_to_readme(rainfall_data, title="ปริมาณฝนสะสม 3 วัน", mode="a")
    
