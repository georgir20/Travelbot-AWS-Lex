
This repository provides the whole code of a travel bot (chat bot) that I created as part of the project course “advanced web technologies” at TU Berlin. The travel bot which was built in AWS Lex guides the user through a tour in India while providing recommendations for a hotel and train connections. The installation guideline for the travel bot can be found below. The goal of the overall project course was to compare multiple bot frameworks. The final results of this course can be seen in the presentation which was created with my fellow students Sadaf Yazdanparast and Julius Kaiser.  
The AWS Lex bot and all the according source code was created solely by me. 








<h1 align="center">AWS Lex Travelbot</h1>
<h2 align="center">Advanced Web Technologies - Project </h2>
<h3 align="center">Voicebot: Speech-To-Text-To-Speech Components - Group 2</h3>
<h4 align="center">Used AWS Services: Lex, Athena, Lambda, S3; Other Services: Slack</h4>
<h4 align="center">Supervisor: Dr. Christopher Krauss (Fraunhofer FOKUS)</h4>

---

> This readme document presents the installation guideline for a voicebot in the application setting of a travelbot for India. The travelbot is based on multiple AWS services and the bot interface is implemented in AWS Lex.  
---

## Table of contents

<!-- TOC -->

- [Description](#Description)
- [AWS Account Creation](#Aws-Account-Creation)
- [Create S3 Folders and Save Datasets](#Create-S3-Folders-and-Save-Datasets)
- [Create Athena Database and Tables](#Create-Athena-Database-and-Tables)
- [IAM Role Creation](#IAM-Role-Creation)
- [AWS Lambda Function Creation](#AWS-Lambda-Function-Creation)
- [AWS Lex Bot Import](#AWS-Lex-Bot-Import)
- [AWS Lex Bot Build](#AWS-Lex-Bot-Build)


<!-- /TOC -->

---

## Description 

The travelbot helps the user to find any desired train connection to get from point A to B inside of India. 
The travelbot also helps the user to find the name and address of a hotel in India that fullfills the prerequisites of the user. Lastly it can also help to find the right train to get to the chosen hotel.

---


## AWS Account Creation

To start working with the AWS based travelbot, you first need to create an account on AWS. Please go to the 

<a href="https://signin.aws.amazon.com/signin?redirect_uri=https%3A%2F%2Fconsole.aws.amazon.com%2Fconsole%2Fhome%3Ffromtb%3Dtrue%26hashArgs%3D%2523%26isauthcode%3Dtrue%26state%3DhashArgsFromTB_us-east-1_3f1698b34b0717b5&client_id=arn%3Aaws%3Asignin%3A%3A%3Aconsole%2Fcanvas&forceMobileApp=0&code_challenge=5kyfLfrfisPnUBqotVSFT0QsgGGBm3kFAQiiwmubeOI&code_challenge_method=SHA-256">AWS website
 </a> and create an account. Please use as an orientation the following screenshots.

<a 
    title="Project"
    target="_blank"
    href="./Travelbot AWS Lex Source Code/Instruction Screenshots/AWS Account Creation 1.jpg">
    <img 
      alt="Banner"
      src="./Travelbot AWS Lex Source Code/Instruction Screenshots/AWS Account Creation 1.jpg"
      width="400" 
      height="600">                                                      >
</a>

<a 
    title="Project"
    target="_blank"
    href="./Travelbot AWS Lex Source Code/Instruction Screenshots/AWS Account Creation 2.PNG">
    <img 
      alt="Banner"
      src="./Travelbot AWS Lex Source Code/Instruction Screenshots/AWS Account Creation 2.PNG" 
    >
</a>

---

 
## Create S3 Folders and Save Datasets
After you have created the account please go to the S3 (Simple Storage Service) area of AWS.
Please create S3 buckets with the following names that you can see in the picture.
Then open the S3 bucket "AWT Voicebot".

<a 
    title="Project"
    target="_blank"
    href="./Travelbot AWS Lex Source Code/Instruction Screenshots/AWS Lex Travelbot - S3 Storage Buckets.jpg">
    <img 
      alt="Banner"
      src="./Travelbot AWS Lex Source Code/Instruction Screenshots/AWS Lex Travelbot - S3 Storage Buckets.jpg" 
    >
</a>

As seen in the second picture. Create a data folder and open it. 

<a 
    title="Project"
    target="_blank"
    href="./Travelbot AWS Lex Source Code/Instruction Screenshots/S3 Data Folder.PNG">
    <img 
      alt="Banner"
      src="./Travelbot AWS Lex Source Code/Instruction Screenshots/S3 Data Folder.PNG" 
    >
</a>

In the data folder. Create the new folders: "hotels_in_india" and "trains_in_india". 
In the "india_hotels" folder, please upload the dataset file "hotels_in_india_used.csv"
In the "india_trains" folder, please upload the dataset file "trains_india_used_final_new2.csv"
An example can be seen below. 

<a 
    title="Project"
    target="_blank"
    href="./Travelbot AWS Lex Source Code/Instruction Screenshots/india_hotels folder.PNG">
    <img 
      alt="Banner"
      src="./Travelbot AWS Lex Source Code/Instruction Screenshots/india_hotels folder.PNG" 
    >
</a>

---


## Create Athena Database and Tables
Now after you have uploaded the .csv Files you can build the database and tables thar are necessary for the travelbot to work with data from the datasets. Please go to the AWS Athena Service Overview.

Please insert the statement "CREATE DATABASE awt_voicebot_india" in query editor and click on "Run" to create the database.

<a 
    title="Project"
    target="_blank"
    href="./Travelbot AWS Lex Source Code/Instruction Screenshots/AWS Athena.PNG">
    <img 
      alt="Banner"
      src="./Travelbot AWS Lex Source Code/Instruction Screenshots/AWS Athena.PNG" 
    >
</a>


After the database is created. Please take the code from the SQL-Files that are saved in the project folder: "Athena Table Creation Queries".
Put the SQL Statements into two separate query editor windows and click on "Run" for both of them. That will create the two tables for hotels and trains that are the underlying bases of the travelbot. 

---

## IAM Role Creation

In the following step you need to create an Identity and Access Management (IAM) role. That is then implemented in the Lambda Functions that are mentioned in the next part. The IAM Role allows the lambda functions to have access to the different AWS services (S3, Athena). 
Please go the the IAM Service Overview. There please click on "Create Role"/"Rolle Erstellen".

<a 
    title="Project"
    target="_blank"
    href="./Travelbot AWS Lex Source Code/Instruction Screenshots/IAM Role Service Overview.PNG">
    <img 
      alt="Banner"
      src="./Travelbot AWS Lex Source Code/Instruction Screenshots/IAM Role Service Overview.PNG" 
    >
</a>

Please name the role "indian_hotels_role2" as it is embedded with this clarification already in the AWS Lambda functions. Than please add the following permissions/Berechtigungen that are visible in the screenshot below. 

<a 
    title="Project"
    target="_blank"
    href="./Travelbot AWS Lex Source Code/Instruction Screenshots/IAM role - hotels_in_india2 .PNG">
    <img 
      alt="Banner"
      src="./Travelbot AWS Lex Source Code/Instruction Screenshots/IAM role - hotels_in_india2 .PNG" 
    >
</a>
--- 

## AWS Lambda Function Creation
After you have created the IAM access role you can now create all necessary Lambda function that the AWS Lex bot uses. Please go to the AWS Lambda service overview. Please create all following functions that you can see in the screenshot below. You can do that through clicking on the button "Create Function/Funktion Erstellen". 

<a 
    title="Project"
    target="_blank"
    href="./Travelbot AWS Lex Source Code/Instruction Screenshots/Lambda Functions Overview.PNG">
    <img 
      alt="Banner"
      src="./Travelbot AWS Lex Source Code/Instruction Screenshots/Lambda Functions Overview.PNG" 
    >
</a>

When you create the Lambda function please pay attention to always select the following presettings.
<a 
    title="Project"
    target="_blank"
    href="./Travelbot AWS Lex Source Code/Instruction Screenshots/Create Lambda Function PreSettings.PNG">
    <img 
      alt="Banner"
      src="./Travelbot AWS Lex Source Code/Instruction Screenshots/Create Lambda Function PreSettings.PNG" 
    >
</a>

Make sure the run time/Laufzeit is always Python 3.9 and the access role is the IAM role "indian_hotels_role2" that you created in the previous part. After you have created the role, please open the Code area. Delete all code that might  written in there before. Go to the project folder 
"Lambda Functions" and take the python code that is associated with the according Lambda function and paste it into the Lambda code area. 
<a 
    title="Project"
    target="_blank"
    href="./Travelbot AWS Lex Source Code/Instruction Screenshots/Lambda Function Code Pasting.PNG">
    <img 
      alt="Banner"
      src="./Travelbot AWS Lex Source Code/Instruction Screenshots/Lambda Function Code Pasting.PNG" 
    >
</a>

After you have pasted in the code go the Configuration/Konfiguration area. There go to the sub area "basic settings/configuration" and change the Timeout and the Arbeitsspeicher/main memory to the values which you can see in the screenshot below. 
Finally go back to the Code area and click on "Deploy".

<a 
    title="Project"
    target="_blank"
    href="./Travelbot AWS Lex Source Code/Instruction Screenshots/Lambda Function General Configuration.jpg">
    <img 
      alt="Banner"
      src="./Travelbot AWS Lex Source Code/Instruction Screenshots/Lambda Function General Configuration.jpg" 
    >
</a>

---

## AWS Lex Bot Import
After you have created the database tables in AWS Athena and implemented all Lambda Functions you can now import the AWS Lex bot.
This will import all the intents, prompts and slots of the AWS Lex travelbot. The lambda functions are already predefined in the intents.

Please go to the AWS Lex service overview. 
On the bot overview page please click on the "Action" button. 
<a 
    title="Project"
    target="_blank"
    href="./Travelbot AWS Lex Source Code/Instruction Screenshots/AWS Lex Bot Overview.PNG">
    <img 
      alt="Banner"
      src="./Travelbot AWS Lex Source Code/Instruction Screenshots/AWS Lex Bot Overview.PNG" 
    >
</a>

Then click on import and the bot import pop-up will open. In this pop-up please click on the "Browse" button and select the following .zip file that you can find in the project folder: "AWT_Voicebot_3_208b4ba9-4435-48ec-99c8-316d4ff44ac8_Bot_LEX_V1.zip". After you have selected the zipped folder please click on the "Import" button.

<a 
    title="Project"
    target="_blank"
    href="./Travelbot AWS Lex Source Code/Instruction Screenshots/AWS Lex Bot Import.jpg">
    <img 
      alt="Banner"
      src="./Travelbot AWS Lex Source Code/Instruction Screenshots/AWS Lex Bot Import.jpg" 
    >
</a>



---

## AWS Lex Bot Build
After you have imported the bot you should see now the "AWT_Voicebot" in the general AWS Lex bot overview. Please click on our AWT_Voicebot. You can now see the inside overview of the bots. All 20 intents should be visible on the left. 
Now please click on the "Build" button on the top right corner to get our travelbot starting. 

<a 
    title="Project"
    target="_blank"
    href="./Travelbot AWS Lex Source Code/Instruction Screenshots/AWS Lex - Build Bot.PNG">
    <img 
      alt="Banner"
      src="./Travelbot AWS Lex Source Code/Instruction Screenshots/AWS Lex - Build Bot.PNG" 
    >
</a>

The Test bot window should now be visible on the right part of the screen. Type in a greeting statement to start interacting with the travelbot.

<a 
    title="Project"
    target="_blank"
    href="./Travelbot AWS Lex Source Code/Instruction Screenshots/AWS Lex Bot Interaction.PNG">
    <img 
      alt="Banner"
      src="./Travelbot AWS Lex Source Code/Instruction Screenshots/AWS Lex Bot Interaction.PNG" 
    >
</a>


