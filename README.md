# pyJiraKPI

>  Please make sure your setup is complete

## KPI Notes

  1.  At the bottom of the kpi.py file, there is a section that needs to be updated according to the kpis you are running.

        ```
        store.year = 2020
        store.month = 12
        store.project = 'HCMAT'
        store.rapid_view = '260'
      ```

      year and month are self explanatory, project is the JIRA project which you are using to get your data.  The rapid view is visible in jira in the url when viewing  scrum board your using to manage your team.

      ![image](https://user-images.githubusercontent.com/63073403/105727818-75229380-5ef9-11eb-8c84-8225af0fb933.png)

## To Execute

  1. Right now you can simply run the kpi.py file.
  
    python kpi.py

  2. Option 2 - in vscode you can hit Ctrl-Shift-P with kpi.py open in the editor.

![image](https://user-images.githubusercontent.com/63073403/105728267-f548f900-5ef9-11eb-90cd-117346fc4259.png)

  the code produces and output in csv format in the output.  Currently, I copy and paste it over one of the csv files in the project.

## Setup 

1. Install IDE
   
    This isn't technically required.  Python parses and interprets plan old text files, but it definitely makes things easier.  I suggest Visual Studio Code

    https://code.visualstudio.com/Download

    If you choose to use vs code, you need to install the python extension.

    * Click the entensions icon on the toolbar:
      
      ![image](https://user-images.githubusercontent.com/63073403/105726351-fb3dda80-5ef7-11eb-9852-f513885abd1a.png)

    * Search for python in the marketplace
  
      ![image](https://user-images.githubusercontent.com/63073403/105726623-41933980-5ef8-11eb-91f1-75dc44cb7008.png)

      click install on the Python extension from microsoft.

      When opening this project, I would suggest "Open directory" where VS code will load all the required files.

2. Install Python 3.x
   
   Install python, however you'd like, I prefer winget/chocolaty  but it's your machine. ( https://www.python.org/downloads/ )

   To test your installation, type "python" on the command promp and you should get the following:

   ![image](https://user-images.githubusercontent.com/63073403/105720836-e4948500-5ef1-11eb-9ae2-541d03ca1f72.png)

    **To exit, Ctrl-Z at the '>>>' prompt**

3. Install Pip ( Python installs packages):

    Pip is the python package manager, similar to nuget, winget, npm, or apt-get.

    1. Check if you have pip installed, at the command promp type "pip help".  If you get help text, skip this section.
    2. goto: https://bootstrap.pypa.io/get-pip.py and copy the text into a file named get-pip.py on your local machine.
    3. open a command line to the location you created the file in #2, and execute.
        ```
        python get-pip.py
        ```
    4. Check your installation by
        ```
        pip --version
        ```
4. Install packages
    1. execute install on command line:
        ```
        pip install aiohttp
        pip install asyncio
        ```
5. Create a Jira API Token
   . Click your avatar in the top right hand corner of Jira, select  Account Settings > Security > "Create and Manage API Tokens"
  ![image](https://user-images.githubusercontent.com/63073403/105718332-1e17c100-5eef-11eb-8e06-e0c72c734994.png)
    > Keep that value safe, you cannot see it again once you've created it.  ( You can alway create a new one )*

  1. Create a .env file on the root folder.  This will allow you to access these values as part of configuration, and not in the code.

      ```
      JIRA_API_KEY=<your api key>
      JIRA_USER=<email address for jira account>
      JIRA_BASE_URL='frontlinetechnologies.atlassian.net'
      ```
      > note - don't add single quote around they user, or key values.

