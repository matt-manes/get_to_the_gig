# getToTheGig
WIP<br>
getToTheGig is a program/framework for scraping the event calendars of venues and centralizing them in a database 
so you can find something to do without having to check all the websites yourself.<br>
<br>
Requires Python >= 3.10<br>
Some of the scrapers require the use of selenium so Firefox and the appropriate web driver needs to be installed as well.<br>
The web driver should be in your PATH or in the getToTheGig directory.<br>
It can be obtained here: https://github.com/mozilla/geckodriver/releases <br>
<br>
After cloning this repository, run the setup.py script.<br>
Currently all the venues in shows.db are local to Chicago, IL.<br>
<br>
To scrape all the venues, simply run the scrape_venues.py script.<br>
scrape_venues.py has one optional command line argument and it is -t/--threads to set the number of scrapers to run in parallel.<br>
The default is 10, but you may want to adjust it according to your hardware (parallel selenium instances can eat up a lot of ram).<br>
<br>
<br>
The scraped events can be viewed using the cli script whats_happening.py<br>
Running <pre>python whats_happening.py -h</pre> produces:
<pre>
usage: whats_happening.py [-h] [-da [DAYS_AWAY ...]] [-dotw [DAY_OF_THE_WEEK ...]] [-v [VENUES ...]] [-i] [-sb SORT_BY]

options:
  -h, --help            show this help message and exit
  -da [DAYS_AWAY ...], --days_away [DAYS_AWAY ...]
                        Expects one or two arguments. If one argument is passed, only events that many days away will be shown. If two arguments are passed, events within those many
                        days, inclusive, will be shown. i.e. "-da 0 7" will show events between today and 7 days from now.
  -dotw [DAY_OF_THE_WEEK ...], --day_of_the_week [DAY_OF_THE_WEEK ...]
                        Show events by day of the week name. i.e. "-dotw friday" will show events for the upcoming friday. (If the current day is friday, it will show events for the
                        following friday.) If today is tuesday and "-dotw friday thursday" is used, the results will events between friday and the thursday after this friday,
                        inclusive. If this arg is provided alongside -da/--days_away, -da/--days_away will be ignored.
  -v [VENUES ...], --venues [VENUES ...]
                        Only show these venues in the results. Any venue names with spaces in it must be enclosed in quotes.
  -i, --info            Show event info column in output.
  -sb SORT_BY, --sort_by SORT_BY
                        Sort the output by this column.
</pre>
The default behavior (running whats_happening.py without arguments) is to show you what events are happening today.<br>
At the time of writing, this produces:
<pre>
+---------------------+------------------+-----------------------------------------+---------+-----------------------------------------------------------------------------------------+
| date                | venue            | acts                                    | price   | event_link                                                                              |
+=====================+==================+=========================================+=========+=========================================================================================+
| 2023-01-03 20:00:00 | Schubas Tavern   | feeble little horse Merce Lemon Hemlock | $13.00  | https://lh-st.com/shows/01-03-2023-feeble-little-horse/                                 |
+---------------------+------------------+-----------------------------------------+---------+-----------------------------------------------------------------------------------------+
| 2023-01-03 21:00:00 | Beat Kitchen     | Chicago Underground Comedy              | $10.00  | https://www.beatkitchen.com/event-details/11734315/chicago-underground-comedy           |
+---------------------+------------------+-----------------------------------------+---------+-----------------------------------------------------------------------------------------+
| 2023-01-03 21:00:00 | Beat Kitchen     | Chicago Underground Comedy              | $10.00  | https://www.beatkitchen.com/event-details/11734315/chicago-underground-comedy-canceled- |
+---------------------+------------------+-----------------------------------------+---------+-----------------------------------------------------------------------------------------+
| 2023-01-03 21:00:00 | The Empty Bottle | Rent Control Records DJ Set             | Free    | https://eventbrite.com/e/501065669907                                                   |
+---------------------+------------------+-----------------------------------------+---------+-----------------------------------------------------------------------------------------+
</pre>
Another example (for reference today is tuesday january 3rd):
<pre>
>py whats_happening.py -dotw thursday sunday -v "sleeping village" "golden dagger"
+---------------------+------------------+-----------------------------------------------------+------------------------+--------------------------------------------------------------------------------------------------+
| date                | venue            | acts                                                | price                  | event_link                                                                                       |
+=====================+==================+=====================================================+========================+==================================================================================================+
| 2023-01-05 19:30:00 | Sleeping Village | Big Ass Sketch Revue                                | ADV $10 / DOS $15      | https://sleeping-village.com/event/big-ass-sketch-revue/                                         |
+---------------------+------------------+-----------------------------------------------------+------------------------+--------------------------------------------------------------------------------------------------+
| 2023-01-05 19:30:00 | Sleeping Village | Big Ass Sketch Revue                                | ADV $10 / DOS $15      | https://sleeping-village.com/event/big-ass-sketch-revue/sleeping-village/chicago-illinois/       |
+---------------------+------------------+-----------------------------------------------------+------------------------+--------------------------------------------------------------------------------------------------+
| 2023-01-05 20:00:00 | Golden Dagger    | 5 R V L N 5 Dyslexicon The Feral Ghosts             | $10.00                 | https://goldendagger.com/event-detail/12734635/5-r-v-l-n-5-dyslexicon-the-feral-ghosts           |
+---------------------+------------------+-----------------------------------------------------+------------------------+--------------------------------------------------------------------------------------------------+
| 2023-01-06 20:00:00 | Golden Dagger    | Spizm Doc Wattson Greenlights Music                 | $10.00                 | https://goldendagger.com/event-detail/12685965/spizm-doc-wattson-greenlights-music               |
+---------------------+------------------+-----------------------------------------------------+------------------------+--------------------------------------------------------------------------------------------------+
| 2023-01-06 21:00:00 | Sleeping Village | Dasani Boys                                         | $Main Bar - Free Event | https://sleeping-village.com/event/dasani-boys/                                                  |
+---------------------+------------------+-----------------------------------------------------+------------------------+--------------------------------------------------------------------------------------------------+
| 2023-01-07 13:00:00 | Golden Dagger    | Open House                                          | $0.00                  | https://goldendagger.com/event-detail/12490245/open-house-open-decks                             |
+---------------------+------------------+-----------------------------------------------------+------------------------+--------------------------------------------------------------------------------------------------+
| 2023-01-07 20:00:00 | Golden Dagger    | 7000 F.A.B.L.E. Deezyy                              | $13.00                 | https://goldendagger.com/event-detail/12745585/7000-f-a-b-l-e-deezyy                             |
+---------------------+------------------+-----------------------------------------------------+------------------------+--------------------------------------------------------------------------------------------------+
| 2023-01-07 21:00:00 | Sleeping Village | TOKYO DISCO                                         | $Main Bar - Free Event | https://sleeping-village.com/event/tokyo-disco-4/                                                |
+---------------------+------------------+-----------------------------------------------------+------------------------+--------------------------------------------------------------------------------------------------+
| 2023-01-08 14:00:00 | Golden Dagger    | Kabir Dalawari IndigoesBlue                         | $10.00                 | https://goldendagger.com/event-detail/12738885/kabir-dalawari-indigoesblue                       |
+---------------------+------------------+-----------------------------------------------------+------------------------+--------------------------------------------------------------------------------------------------+
| 2023-01-08 20:00:00 | Golden Dagger    | Cocoa Greene Big Gidz & Meghavahana Will Wisniewski | $10.00                 | https://goldendagger.com/event-detail/12738875/cocoa-greene-big-gidz-meghavahana-will-wisniewski |
+---------------------+------------------+-----------------------------------------------------+------------------------+--------------------------------------------------------------------------------------------------+
</pre>
