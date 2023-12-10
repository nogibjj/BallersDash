# NBA Statistics Dashboard

## The NBA Statistics Dashboard is an immersive and dynamic analytics tool that empowers users with in-depth insights into NBA teams and players, utilizing head-to-head analytics, raw statistics, dynamic visualizations, and advanced ranking algorithms. Showcasing a user-friendly interface for analyzing gaming trends, making informed decisions for fantasy league gameplay, and enhancing the sports betting experience.

### Team Members: Rakeen Rouf, Osama Ahmed, Faraz Jawed, Simrun Sharma

### Project Overview

The NBA Statistics Dashboard is an innovative and user-focused project that harnesses daily data scraping to create a dynamic platform for NBA enthusiasts, fantasy league participants, and sports bettors. This cutting-edge tool offers a rich set of functionalities, including head-to-head analytics, raw statistics exploration, interactive visualization, team ranking insights, probability distribution graphs, point difference analytics, real-time injury updates, and dynamic raw stats graphs. By providing a comprehensive and customizable view of NBA team dynamics, the dashboard redefines the landscape of NBA statistics, empowering users to make informed decisions in fantasy leagues and sports betting.

### Data Source: [Basketball References]

On Basketball Reference, you can find:

- **Player Statistics:** Detailed individual player statistics, including points, rebounds, assists, steals, blocks, shooting percentages, and more.

- **Team Statistics:** Comprehensive team performance metrics, standings, and historical data.

- **Game Logs:** Game-by-game logs for both players and teams, showcasing their performance in each match.

- **Historical Data:** Extensive historical data for seasons, playoffs, and championships.

- **Player and Team Comparisons:** Tools for comparing the performance of different players or teams.

- **Advanced Statistics:** Advanced analytics and metrics that go beyond basic box scores.

- **Player and Team Records:** Records and milestones achieved by players and teams throughout NBA history.

- **Trade and Transaction History:** Information on player trades and transactions.

# Detailed ETL Pipeline Workflow

Our ETL (Extract, Transform, Load) pipeline orchestrates a seamless flow of data from Basketball Reference to our Azure Databricks SQL Warehouse, enriching it with analytics. Here's an in-depth breakdown:

## 1. Data Extraction:
   - The process commences by extracting raw team data from Basketball Reference, a prominent sports statistics website.
   - This data spans a variety of attributes, encompassing player statistics, team performance metrics, and detailed game information.

## 2. Transformation with Spark:
   - Extracted data undergoes transformation using the powerful capabilities of Apache Spark.
   - Leveraging Spark DataFrames, we structure, clean, and manipulate data efficiently, enabling complex calculations and aggregations on large datasets.

## 3. Loading into Azure Databricks SQL Warehouse:
   - Transformed data finds its home in our Azure Databricks SQL Warehouse, a scalable and performant database solution.
   - Within the SQL Warehouse, structured tables facilitate easy querying, forming the foundation for subsequent analytics.

## 4. Scheduled Trigger at 6 AM:
   - The ETL workflow operates on a daily schedule, triggered precisely at 6 AM.
   - This automated execution ensures our database receives regular updates, guaranteeing that analytics are consistently based on the latest information.

## 5. Python Logic Script on Azure Databricks Cluster:
   - A Python logic script serves as the orchestrator, connecting to our Azure Databricks cluster.
   - This script acts as a bridge between stored data and the analytical functionalities, facilitating a seamless flow through the pipeline.

## 6. Analytics and Web App:
   - The analytics phase encompasses a spectrum of calculations and insights derived from the processed team data.
   - User-friendly interfaces on our web application provide a rich environment to explore player performance metrics, team comparisons, historical trends, and advanced analytics.

By synergizing the capabilities of Apache Spark, Azure Databricks, and a meticulously designed ETL pipeline, our sports analytics platform ensures a robust and up-to-date foundation. Users gain valuable insights and make informed decisions, navigating the intricate world of basketball with ease.


#### Text Related Graphs
To go beyond the telemetry provided by the Steam Platform, we generated two types of graphs based on the text data in the reviews of our video games. The two graphs are clustered using tokenization, TFIDF Vectorization and then MiniBatchKmeans with 3 clusters. This methodolgy is meant to identify like reviews and group them together, so that developers can highlight issues or positive traits about their game in a snapshot. These cluster results were then outputted in two forms: a word map and a bar chart. See the description below. 
![Alt text](images/cloud0.png)![Alt text](images/cloud1.png)![Alt text](images/cloud2.png)

The wordmap graphs display the three clusters generated from the clustering scripts. It ouputs the most frequented words talked about within each cluster. The larger the size the more it was talked about. The title at the top is a review which was written by a user that is the most representative of that cluster. Therefore, this is the title of that cluster. It is really interesting to see the different groupings of reviews and how closely they are related to the title.
![Alt text](images/clustering.png)


This bar plot is a list of the most said 3 word phrases within cluster. We see a lot of more common game problems, economics, or developer problems in these trigrams. Therefore developers can look more into problems and how they should fix them.

### Dashboard Display

The dashboard is fully displayed utilizing the Python package ```Flask```, which is an easy way to combine written Python code and HTML code. The HTML code is necessary to have an attractive interface, with simple UI features, to facilitate the information for thet user. The HTML code was written to have a display page that requests a selection of a game, a date range of interest, and a month/day of interest. 

From here, the microservice displays a "waiting" page, which is meant to indicate to the user that inforamtion is being prepared. Once ready, the microservice will finally show the dashboard itself. This will have a variety of graphs, explained as well, so that the user can interact and understand. There will also be a button to allow the user to enter another game, or change their query selection.

### Data Engineering with Azure

After the user inputs a few parameters, the code will begin its interaction with Azure Databricks. Immediately, the code will check on whether the cluster designated for this project is currently running. If it is not, the code will automatically begin spinning up this cluster. The cluster has a 10 minute inactivity limit for turning off, in attempt to save money. If the cluster is currently running, it will then execute a SQL query. This SQL query will be unique, as it will combine a pre-set skeleton with the user inputs. After query execution, the data will be saved as a ```pandas``` DataFrame. The reason this data structure was chosen was due to its easy compatibility with ```plotly```, which was used to create the interactive graphs. The added benefit of utilizing Azure Databricks was to be able to utilize an effective, and powerful, Infrastructure as Code (IaC) solution.

### Docker

This project is currently contained on DockerHub, accessible with this link https://hub.docker.com/repository/docker/kbagherlee22/steam_review_analyzer/general

 The Dockerfile, currently located in ```src/web_app```, is used to make the DockerImage for the entire microservice. From here, the container is pushed to Azure Web App, so that the entire dashboard can be deployed to a public endpoint. With this public endpoint, it becomes easier for anyone to access the dashboard. The utilization of Docker and Azure Web App was paired with the thought of, once the pipeline was established, the entire dashboard becomes easily scaleable.

 The following are Key Metrics from the Azure Web App, to demonstrate that the container was correctly pushed and deployed to a public endpoint.

 ![image](https://github.com/nogibjj/Steam_Review__Analyzer/assets/55768636/ef0bbcce-0c83-4a97-9e1c-6097bc9e37a1)

### GitHub Actions

The group implemented a GitHub Actions to promote a CI/CD pipeline. The checkpoints that were established was utilizing ```Ruff``` to lint the code, ```Black``` to format the code, a tester to ensure that all packages were properly downloaded from the ```requirements.txt``` file, and ```PyTest``` as our actual code tester. The group did not stop until it was ensured that everything was passed, functioning properly, and looked presentable. This projects GitHub badges are shown above.

### Load Testing and Quantitative Assessment

As this application could forsee a future with mutliple users, the group decided to load test. Utilizing ```locust```, the group was able check how many users the application can withstand before failing. Setting a maximum of 1,000 users attempting to utilize the microservice, the results below show how successful the entire project was of withstanding a large amount of incoming traffic. The code displaying the behaviors each of these users did is represented in ```locustfile.py```.

![Alt text](images/image.png)

Along with withstanding a large amount of users, the team felt it would be a success if the average latency per request was anywhere below a minute. This is under the condition that the cluster was already spun, as it takes ~5 minutes for the cluster to initially be created, which severely impacts the latency. The following graph below shows the success.

![Alt text](images/image-1.png)

### How to Run the Project

A big question remains: How can one run this application locally? To run, all that needs to be performed are the following steps.

1. Clone this respository
2. Run ```make install```, to get the Python version, as well as all the packages, running on your local device
3. Either run directly from ```app.py```, or utilize the ```Flask``` CLI, and set ```FLASK_APP=app.py```, then run ```flask run```

From there, you will get to see the entire application from local. This is also due to the .devcontainer configuration that was downloaded from the repository, which allows easy use of this application within GitHub Codespaces.

### Limitations and Potential Improvement

There were many limitations that occured throughout the creation of this project. First is related to the actual data collection itself. Steam's API is limited on how many requests can be made, where each review is a request to their system. As a result, after a good amount of reviews, the system would place the request under a "timeout" that lasted ~5 minutes. This made data collection a long and strenuous process, as well as made it time consuming to request the reviews for more popular games.

The second limitation came with the reviews themselves. Sometimes the reviews had nothing to do with the games themselves, and were used to make a joke. Other times, the review would express immense distaste for the game before labeling their review as positive. A large number of reviews were labelled as being in English and were not, either being written in another language or being full of emojis. 

A third limitation is how slow Azure Databricks takes to spin up a cluster. As a result, if the user is the first person to attempt to access the cluster in ~10 minutes, it will take almost 5 minutes to start up again. This overhead time is paired with the time necessary to perform the other analysis, which could take longer than what any user is willing to wait. Keeping the cluster constantly on is not a valid solution to this problem, as the cost will quickly pile-up. While these issues are tedious, deviating from Azure Databricks as a whole becomes another issue has many decisions were made surrounding the available tools Azure provides.

From this point, there are a few potential improvements. One is moving the entire project infrastructure to AWS, which comes with pros and cons. While it will speed-up the entire latency time, it will also take significant time to learn the tools AWS uses, and port everything over. The second potential improvement is the add a sentiment analysis feature, which will provide a second interactable feature for users. As well, it can be used to derive a more accurate sentiment on the reviews under a game, which was highlighted earlier as a big issue.

### Utilization of AI Pair Programming Tools

Throughout this project, many team members utilized a variety of different AI Pair Programming tools, the two main tools being ChatGPT and GitHub Copilot. These tools were primarily used for debugging purposes, as working with ```Flask``` and HTML as a whole was entirely new for many team members. These tools were able to explain many of the bugs, and offer insight on how one could potentially implement the wishes of the team into HTML.

The other main use was to explain the interaction between any python file and the project cluster/delta table. This is because utilizing the Databricks REST API was initially difficult, and many approaches were found online with little success. These tools were able to offer a single method, which was then suplemented with the implemetation needed for this project. 

### Architectural Diagram

![image](https://github.com/Ninsta22/Steam-Review-Dashboard/assets/55768636/c568a469-cd79-4131-bdbb-a9810b9e7d05)

### Demo Video

{PLACE DEMO VIDEO HERE}