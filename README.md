# News Aggregator

## Overview

Let's jump right into it. A set of microservices which save users' preferences and send them news digests on request, using Telegram Bot as the delivery medium. The purpose is to provide users a convenient way to consume only news they could be interested in, and only when it is comfortable, without clickbaits and distracting colorful banners. The application uses AI to analyze which news suits you best and then creates short digests with news URLs you can click to find out more if the news appeals to you.

### Technologies used

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![DAPR](https://img.shields.io/badge/DAPR-blue?logo=dapr&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-green?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-blue?logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-blue?logo=docker&logoColor=white)
![Logging](https://img.shields.io/badge/Logging-blue?logo=logging&logoColor=white)
![Semantic Kernel](https://img.shields.io/badge/Semantic_Kernel-blue?logo=semantic-web&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-blue?logo=pydantic&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-red?logo=redis&logoColor=white)
![WorldNewsAPI](https://img.shields.io/badge/WorldNewsAPI-blue?logo=news&logoColor=white)
![OpenAI API](https://img.shields.io/badge/OpenAI_API-blue?logo=openai&logoColor=white)
![aiogram](https://img.shields.io/badge/aiogram-blue?logo=telegram&logoColor=white)
![bcrypt](https://img.shields.io/badge/bcrypt-blue?logo=bcrypt&logoColor=white)
![Swagger](https://img.shields.io/badge/Swagger-API-green?logo=swagger)

### Bird’s-eye view

The service consists of 7 microservices in separate containers as shown in the diagram.

![application scheme](https://github.com/holohup/zionnet_news_aggregator/blob/main/img/diagram.png?raw=true)

A **DAPR sidecar** is riding next to each container, helping with *service discovery*, *secrets storage*, *sync*, and *async* communications using gRPC and Message Queue. It takes care of message delivery retries and a lot of other under-the-hood details. Nearly every action is logged, which tremendously helps with debugging. The project also includes some integration tests to verify everything is working after startup.

## How to run

Clone the repository. Make sure you have a *secrets/secrets.json* file. We will touch on that later. After everything's downloaded, do a
```sh
docker compose up
```
If you happen to have a spinning hard drive, it may make some noise while building the images, and the app should greet you with a lot of logging information.

## Showcase scenario

1. Start a chat in the Telegram Bot

- [@zionnet_bot](https://t.me/zionnet_bot) - click on the link, or enter the bot name in Telegram Search. You will find it immediately.
- Press the 'Start' button. The Bot will send you a response with your chat ID.

![bot response with id](https://github.com/holohup/zionnet_news_aggregator/blob/main/img/bot.png?raw=true)

This is the number you will need when registering - it is required to send you the news digest when you request it, so copy it to the clipboard.

2. Register in the service

- Go to http://127.0.0.1:8000/docs/ - it is the Swagger interface for the REST API, which we will use. *It is handy to use another browser to be able to switch between these instructions and the API interface using ALT-Tab, without the need to switch between single browser tabs*.

- Open the first '/user/register' endpoint and click on the 'Try it out' button.

![try it out](https://github.com/holohup/zionnet_news_aggregator/blob/main/img/registration.png?raw=true)

You need to provide your email (used as a unique identifier for each user), password (to generate a JWT token), contact info (currently - the former step Telegram Bot chat ID), and the self-description. The description is critical to how the service works - the more specific it is, the more tailored the news will be. Please try to specify as many details about yourself as you can. These details will be used:
    1. To generate tags, which are used to parse news that might interest you using AI.
    2. Again with the help of AI, both the description and tags are used to validate the news and choose only the most interesting ones.
When you press the 'Execute' button, you will be registered instantly. In the background, a process will launch to fill out the tags for you. You can see that in the response (which fetches the user info from the DB), the 'tags' field in 'settings' is empty.

![empty tags](https://github.com/holohup/zionnet_news_aggregator/blob/main/img/empty_tags.png?raw=true)

This will change when you authorize in the next step. After that, you can check the 'me' endpoint.

![filled tags](https://github.com/holohup/zionnet_news_aggregator/blob/main/img/filled_tags.png?raw=true)

If you feel like your tags are misleading or don't describe you holistically, you can always fine-tune them. The tag generation is a one-time procedure for each new registration, needed to provide service ASAP without forcing the user to think of tags that describe them.

3. Authorize with your credentials and get a JWT token.

Luckily, the Swagger UI provides a way to do it in a browser without editing JSONs and continue using the service.
- Scroll to the top of the page and click on the "Authorize" button in the top-right corner.

![authorize button](https://github.com/holohup/zionnet_news_aggregator/blob/main/img/authorize.png?raw=true)

- Enter your email in the 'Username' field and password in 'Password', click 'Authorize', and you're in.

Now you can access all the endpoints except the ones restricted to admins only (delete user, get info about the user).

You can also test token generation in the '/token' endpoint if you wish and use it to test the API using other instruments, such as Postman.

4. *(optional)* Change your settings.

You can tune the settings to your liking or continue as is. In '/user/update_settings', you can change four settings:

- Your user *info* (we talked about it earlier).
- *tags* - as explained before, they are needed for correct news parsing and validation. The tags should be separated by a comma.
- *max_sentences* - maximum number of sentences in each news summary the AI generates.
- *max_news* - maximum number of news in each digest.

5. Get that digest at last!

Click on the '/digest' endpoint -> 'Try it out' -> Execute.
You can enjoy the logs flow while waiting for the digest, but it should not take more than 10-20 seconds to receive your news digest from the Telegram bot.
The service remembers the last news processed, so if you immediately request another digest, no new news will be available - you either will have to wait some time for the new news to appear in the service or register a new user.

## How to test

- There're some integration tests included. They check if the microservices interact with each other correctly.
    1. Make sure you have Python (tested with 3.11) installed.
    2. Create a virtual environment, install the dependencies from requirements.txt in the root of the project folder:
    ```sh
    python3.11 -m venv venv && source venv/bin/activate && pip install -r tests/requirements.txt
    ```
    3. Make sure you have your **docker compose up** running.
    4. Execute the tests:
    ```sh
    pytest
    ```

- You can also register an admin user and check endpoints available to admins. To do that, add the admin email to 'secrets/secrets.json' in the **"ADMIN_EMAILS"** field. It's a comma-separated string.
For more in-depth testing, you would need to dive deeper into the application mechanics and settings, which we will cover in the next step.

## Details and components highlights

All services follow more or less the same structure. There's a *main.py* file which is an entrypoint, a *config.py* which defines how the service behaves and some constants needed for it to function. When the microservice is big enough, it usually has a layer of abstraction to make both higher-level modules and low-level implementations depend on it. The only exception is the report sender service, telegram accessor, which is so small it has nearly everything in main.py. All code is available in the *src* folder.

### api_gateway

The user-facing REST API, the only way to make the service do something, the only container with port open to the outer world. Its main functions are:
- provide first-level validation (like is the email valid? is the JWT token legitimate?) and authentication
- choose which manager to pass the request to or ask about the user's request
- deliver results which are available instantly or exceptions with permitted details to the user

It does not implement any logic of its own except for that and only passes the information back and forth.

### user_manager

Deals with stuff related to users - CRUD operations, data to validate tokens. It knows how to communicate with the **db_accessor** which stores the users' information. It also is responsible for sending a tag generation request to **ai_accessor** queue and processing the response for each new user.

### news_aggregation_manager

This manager is responsible for the main functionality of the service. If it grows any bigger, an engine should be extracted from it to a separate microservice (at least the processor class, which incorporates the business logic of digest generation). It is responsible for:
- keeping the news database up to date. On startup and then periodically, it invokes a **news_accessor** method to parse new news and delete the old ones. First, it asks **db_accessor** for all the user tags from all users. Then passes the tags to the **news_accessor** to parse the news about those tags.
- creating the digest. It gets user info from **db_accessor**, stores user contact and email, and sends a message without them to the **ai_accessor**, containing just the user information and tags to generate the digest. When the digest is returned, knowing the user's ID in the message, it retrieves the contact information and sends a message with contact and digest to the **tg_accessor** to deliver the digest. Also, knowing the user's email, it sends a request to **db_accessor** to update the user's last read news timestamp.

Therefore, it has access to and uses all four accessors in the service. The ultimate power!

**!NB** In config.py
```python
news=NewsConfig(pause_between_updates_minutes=60)
```
defines how often the news updater service from news_accessor should be called. It might be a highly volatile parameter, which depends on how many tags you have, what are the API you are working with limits, etc., so it's in the settings.

### tg_accessor

It is just a messenger. Takes the messages from the DAPR Queue and if it's a report, parses it, formats, wraps in beautiful paper, and sends to the user through Telegram.

### ai_accessor

Currently, it works with the OpenAI API. Its main functions are:
- Generate tags from users' info
- Choose the most interesting news and create a digest

In order to lower token consumption, the algorithm for creating a digest works like this:

1. The service gets all the news that appeared since the last time the interested user was creating a digest.
2. The service extracts news titles and summaries if applicable and asks the AI to choose the most interesting ones, given the limits from the user's settings.
3. Only then are the full texts of the news introduced to the AI to create a digest.

When there are thousands of news articles, churning through the full text of each can be both time- and token- (money-) consuming. This algorithm is much faster and cheaper. The tradeoff is in quality, since title + summary can only approximate the news so far.

Given that the service can be slow, all communications with it are asynchronous.
In the config.py 
```python
ai=AIConfig(model_id='gpt-3.5-turbo')
```
it is worth playing with; the **gpt-4o** model is also available, but I haven't tested it yet. The folder *src/ai_accessor/prompt_templates/DigestPlugin* contains the prompts and configs for them.

### db_accessor

Basically, it provides methods to work with users and hides lower-level details under the hood. It currently uses **Redis** as a database (the same Redis is also used as a pub/sub messaging Queue by DAPR). The users are stored using a prefix, so no interference should occur. The microservice implements the **repository** pattern, which allows switching to another database without changing the code.

### news_accessor

This service provides access to the news API. Potentially, there could be gigabytes of news as the user base and amount of tags to parse grow, so I decided not to drag those gigabytes between the services to store them in some database. The service implements a simple **caching strategy** - news are kept in human-readable JSON files. The news expiration time is set in the configuration file; when it comes, the old news are purged from existence on the next update cycle (initiated by **news_aggregation_manager**). Since the update task is a recurring background routine, it also sorts the news after updating by publish date, which helps to search for new news for each user request faster.
The config.py setting
```python
parsing=ParsingConfig(max_entries=100, news_expiration_hours=timedelta(hours=24 * 7), api_key=api_key),
```
sets how long the old news are stored in the database.


## Additional info

### Folders mapped outside the containers

There are a few folders mapped outside for the sake of better understanding how the service behaves and easier backups. They are all in the root folder of the project. Aside from DAPR's components and secrets file storage, there are:

- **logs**: Holds logs for each service, essential for debugging.
- **news**: Contains the news cache file from **news_accessor**, stored as human-readable JSON, along with another file tracking the latest update time to avoid duplicates.
- **redis**: Stores the Redis DB dump, saved every 60 seconds for backup purposes.

### Known issues

- The solution utilizes HTTP, which is not secure.
- Each service has access to secrets, and although they request only what is needed for them, this could potentially be a security vulnerability if someone manages to compromise one of the services.