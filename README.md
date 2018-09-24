# CryptoCatchBot
The original analysis bot that I had running on a Raspberry Pi. It is very basic and was used to teach myself Python. Originally, it used to be my standalone program for analysis; however, I realized I could give the notification more power if I could act on them from anywhere. As a result, I developed a React Native app for this purpose. Also, it has been proven that its analysis technique is weak and unreliable, and it will definitely change in the future to a more advanced regression analysis.

# Development
This program was my introduction to Python. As a result, it went through a few different transitions. 
  
The first phase I did not implement a connection to a database and relied on Excel files. Soon, I found out that data was easily corruptable if an error occured whithout properly closing an Excel file. Therefore, I quickly switched to a database (Postgres) and developed from there. You can still see remnants of code from the Excel days. For instance, CryptoCatch.py file kept the Excel portion because it was easy to quickly deploy a new database on another machine if needed. 

Twilio was used as the first notification system. Their text messages were extremely useful, but they became obsolete once I developed an app with push notifications.

The analysis portion went through a few weak changes, but the one rudimentary method I settled for was to parse for key words. Once a key word was found, it would then scan for other words "paired" to the key word in an attempt to distinguish setiment. It would then take the average percent increase from similar past events and produce an alert accordingly. Overall, it was not very effective. In the future, I hope to implement a more advanced regression analysis or possibly machine learning, but that will have to be once I have more free time.
