- [x] Scrappe workana
- [x] Scrappe 99freela
- [x] Add more jobs targets to scrapper
- [x] Add list to get the selected jobs
- [x] Scrappe freelancer.com
    - [x] add message to telegram and send it!
    - [x] bids less than 10
    - [x] run by filters array
        - [x] limit by 10 jobs per filter
        - [x] add pending jobs only
        - [x] remove client response
        - [/] No database yet
        - [x] add state database
    - [ ] test it!

- [x] Add database to store lists
    - [x] add database to 99freela
    - [x] add database to workana.com
    - [x] add database to freelancer.com
    - [ ] add database to upwork.com

- [x] Add upwork
    - [x] analisys on site
    - [/] find if exists API
    - [x] find if is javascript loaded
    - [x] get jobs details
        - [x] title
        - [x] description
        - [x] price
        - [x] catch fixed price only
    - [ ] Add pagination
    - [x] add filters
        - [x] fixed only
        - [x] add match allowed jobs
        - [x] add state database


- [ ] Add Toogit:
    - [ ] login (with ramdom user)
    - [x] extract jobs
    - [x] add jobs to database
    - [x] filter jobs to only that are NOT in database
    - [x] send jobs to telegram


- view broken sites
    - [ ] upwork.com
        - being detected by system anti-bot
    - [ ] guru
        - requires login
    - [ ] freelancer.com
        - [x] wait too short to load
        - [ ] relocate elements
        - [ ] indentify if is zero jobs and pass
        - [ ] split on class and test it!
    - [x] workana.com
        - drop support