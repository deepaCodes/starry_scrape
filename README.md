# Web scrapping using selenium driver


## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

Python 3.7.0 or higher, I have not tested in previous version of python
Dependency lib's are added into requirement.txt, run dependency.txt to install required python packages.



### Installing and running

A step by step series of examples that tell you how to get a development env running

Install dependency packages 

```
cd <project_root_dir>
pip install -r requirements.txt

```

### Configuration

Sample example configuration file located at <project_root_dir>/scrapper/config.json
```

{
  "web_url": "https://starry.com/#check-availability",
  "chromedriver_path": "E:/chromedriver_win32/chromedriver.exe",  ----> path to your chromedriver.ext
  "headless_mode": "Y",  ---> selenium in headless mode?
  "seconds_to_wait_between_scrape": 5,   --> wait for sec b/w each address scrapping
  "input_address_text_file": "C:/starry_scrape/scrapper/address_list.txt", --- > location of file contining list of addresses
  "output_csv_file_location": "C:/starry_scrape/csv/Starry_Scrape_Results.csv",  ---> where to store output csv file
  "output_text_file_path": "C:/starry_scrape/files",   ---> where to write text files, one file per address
  "retry_count_when_failed": 1,  ---> if the process fail, how many times to retry
  "label_mapping": [
    {
      "text": "Great news",
      "label": "serviceable"
    },
    {
      "text": "Your building can get Starry",
      "label": "petition"
    },
    {
      "text": "We’re on our way!",
      "label": "waitlist"
    },
    {
      "text": "Enter your info below",
      "label": "noservice"
    }
  ]
}

```

### Running

```

python script <project_root_dir>/scrapper/scrape_starry.py <path_to_your_config_file>/config.json

```

## Author

* **Deepa Aswathaiah**