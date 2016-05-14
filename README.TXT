Joseph Paek - jpaek1
Gabriel Giraldo-Wingler - ggirald1

Video Game Metasearch Engine

This metasearch engine searches across Rock30Games.com, GameStop.com, and Ebay.com to
find the lowest prices for every video game, for any console.


Performance:
We found that in testing this, we had huge variance in success, which seemed to depend on the
title of the game. We had great success with Call of Duty, Dark Souls, Legend of Zelda, and
Uncharted, but with other games, though we would get positive responses from the sites,
our data would never get printed. We suspected that it could be a timing issue with our HTTP
protocol, but we're not sure how to go about fixing it. We also found the most success with
our GameStop search, with Ebay following closely behind and Rock30Games falling much
farther back. We also had a bug in our configuration file implementation, so we ended up
hardcoding the links into the program.

We also ran one robot to crawl the three sites, definitely slowing down performance and
accuracy to a certain extent. If we made a robot for each site, our speed probably would have
improved. We also should have used a stronger vector-based model to find the titles of the
queries and the prices in the closest vicinity of it. Perhaps we could have even gone into
the title links and found the price that way in order to increase accuracy, rather than 
finding all of the prices on the search results page and attempting to have them line up
with its corresponding game title.




How to Run:

1) install a local apache server (we used xampp for windows)
2) store videoGameShopper.cgi and config.txt in the appropriate directory (in our case it is in the C:\xampp\htdocs\perl)
3) run xampp and turn on the apache server
4) navigate to localhost\perl\videoGameShopper.cgi in your preffered browser
5) enter the name of the video game you're searching for in the search box
6) hit the 'search' button!
7) enjoy your games!

