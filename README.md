# Finance bot for Telegram

<!-- ![image](https://user-images.githubusercontent.com/18378470/165382677-ca50baa2-b434-4f40-bdd6-54ad7785fc03.png) -->
<img src="https://user-images.githubusercontent.com/18378470/165382677-ca50baa2-b434-4f40-bdd6-54ad7785fc03.png" alt="drawing" width="400"/>

<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
* [Features](#features)
* [How to deploy](#how-to-deploy)
* [Usage](#usage)
* [Contact](#contact)

<!-- ABOUT THE PROJECT -->
## About The Project

This is a simple bot for Telegram. He helps me (and my family) to improve financial discipline. It can handle spendings, and aggregate them to fancy stats. 
For now, it is only self-hosted solution that requires docker and postgresql database. 
Also, it is only Russian language supported, but English is coming soon!

<!-- FEATURES -->
## Features
### Implemented
- Category management (Add, edit, delete, move between category groups)
- Category group management (Add, edit, delete categories)
- Multiple users support: each one can insert spendings and see shared stats
- Stats for any month by category groups and categories
- Daily notifications that reminds to enter spendings 
- Subscriptions management (monthly payments with fixed amount)
- Monthly limits for category groups

### Planned
- Multi-language 
- [Probably] multi-user support (like cloud solution, instead of self-hosted)

<!-- HOW TO DEPLOY -->
## How to deploy
The bot can be deployed with docker.
Here is example for docker-compose service:
```yaml
version: '3.5'
services:
  finance-bot:
    image: benyomin/finance-bot:latest
    links:
      - db
```

### Environment variables
Use them to define mandatory settings and for some customization
| Name        | Description           | Required  | Example |
| ----------- |---------------------|:------------:|--------|
| `BOT_TOKEN`      | Telegram bot token. Obtain it via [BotFather](https://t.me/BotFather) | Yes | 12345:qwerty |
| `DB_DSN`    | [Postgres connection string](https://www.postgresql.org/docs/current/libpq-connect.html#id-1.7.3.8.3.5) | Yes | "host=localhost port=5432 user=postgres password=postgres dbname=finance_bot"
| `ADMITTED_USERS` | Users that allowed to use the bot. Format is string with JSON array of integers | Yes | "[12345, 67890]" |
| `CURRENCY_CHAR` | Currency symbol. | Yes | "$" |
| `IS_REMINDER_ENABLED` | Enable/disable daily reminder. Default value is `true` | No | true |
| `REMINDER_HOUR` | Hour of the day when the reminder should be sent. | No | 21 |
| `REMINDER_MINUTE` | Same as above for minutes | No | 0 |
|`SUBSCRIPTION_HOUR` | Hour of the day when subscriptions should have been processed and user should receive notifications. | No | 10 |
|`SUBSCRIPTION_MINUTE` | Same as above for minutes | No | 0 |

<!-- USAGE -->
## Usage
Since the initial `start` command executed, bot is always listening for amount of spendings.
After amount was sent, the bot will ask user to select category from inline keyboard. Initially it will contain 5 top categoryes by spending counts, but user can navigate categories menu and select the needed one.

Also, the bot supports some commands. Here are they:
- `/categories` — Categories and Category groups management
- `/stats` — Pie plot for current month. Also, can be used with explicit month `/stats month_number` or with explicit month and year `/stats month_number year` 
- `/limits` — Show monthly limits dashboard for category groups with enabled limits

<!-- CONTACT -->
## Contact

* Telegram - [@benyomin](https://t.me/benyomin)  

Project Link: [https://github.com/benyaming/family_finance](https://github.com/benyaming/family_finance)
