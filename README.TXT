Gabriel Giraldo-Wingler - ggirald1
Joseph Paek - jpaek1

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


How to Run:

1) install a local apache server (we used xampp for windows)
2) store videoGameShopper.cgi and config.txt in the appropriate directory (in our case it is in the C:\xampp\htdocs\perl)
3) run xampp and turn on the apache server
4) navigate to localhost\perl\videoGameShopper.cgi in your preffered browser
5) enter the name of the video game you're searching for in the search box
6) hit the 'search' button!
7) enjoy your games!

