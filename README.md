# rpa-nytimes

This is a repository for nytimes developed with Python, [rpaframework](https://rpaframework.org/releasenotes.html).
### Features

1. **Automate Scrap the** [Nytimes](https://www.nytimes.com/)
2. It will search on specific filters.
3. It will download the images of the news
4. It will scrap the news with some details and save it in execl file.
6. Can be test on [robocorp](https://cloud.robocorp.com/)
7. All downloaded images and Excel sheets will be land in **output** folder

## Setup (using python)
1. *pip install -r requirements.txt*
2. *python main.py*

## Setup (using robocorp)

1. [rpaframework](https://rpaframework.org/releasenotes.html)

### Installation

1. Goto [robocorp](https://cloud.robocorp.com/taskoeneg/task/robots) create a bot
2. Add [this](https://github.com/Us-manArshad/nytimes-rpa.git) repo link in public GIT
3. Goto [assistants](https://cloud.robocorp.com/taskoeneg/task/assistants) and add new assistant linked with robot that you had registered above. 
4. Download and install desktop app of robocorp assistant from [there](https://cloud.robocorp.com/taskoeneg/task/assistants) by click on **Download Robocorp Assistant App**
5. Run the assistant you had created above
6. Bot will start performing the task as mentioned above
7. Your output data will be saved in output folder. click on output when task finished.


## File Structure
### [config.py](https://github.com/Us-manArshad/nytimes-rpa/blob/master/config.py)

Keyword | Description
| :--- | :---
URL  | *URL of the nytimes website*
DOWNLOAD_IMAGES_PATH  | *Download directory name*
EXCEL_FILE  | *Excel file path with name name*
SEARCH_TEXT  | *Search text for which you want to scrap the news*
SECTIONS  | *list of sections.*
MONTHS  | *How many older records you want to scrap.*

### [base_bot.py](https://github.com/Us-manArshad/nytimes-rpa/blob/master/base_bot.py)
It will initialize the Main from [main.py](https://github.com/Us-manArshad/nytimes-rpa/blob/master/main.py) instance and call the 
required functions to perform the task.

### [main.py](https://github.com/Us-manArshad/nytimes-rpa/blob/master/main.py)
- Have the logic to search, scrap and create the Excel file for news,
- Get the image links and download the images associated with the news.

### [conda.yaml](https://github.com/Us-manArshad/nytimes-rpa/blob/master/conda.yaml)
Having configuration to set up the environment and [rpaframework](https://rpaframework.org/releasenotes.html) dependencies.

### [robot.yaml](https://github.com/Us-manArshad/nytimes-rpa/blob/master/conda.yaml)
Having configuration for robocorp to run the [conda.yaml](https://github.com/Us-manArshad/nytimes-rpa/blob/master/conda.yaml) and execute the task.py


You can find more details and a full explanation of the code on [Robocorp documentation](https://robocorp.com/docs/development-guide/browser/rpa-form-challenge)
