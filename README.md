# Stock Analysis of Publicly Traded Serie A Clubs  


 _Analysis of the short-term effect of match results on the stock values of three Serie A football clubs over two seasons_  
&nbsp;

## Processes involved

Stock value and match result data over two Serie A seasons; 2017/18 and 2018/19 were sourced for three publicly traded Serie A companies. Results were drawn from two seasons in order to get some idea of year-on-year change for these clubs, as all three remained fairly consistent in table position and competitions over both seasons. Additionally, as external factors may differ significantly year-on-year, comparing data within each season rather than across both seasons seemed more appropriate. The following are those three clubs:

 - Juventus Football Club S.p.A. (Stock Symbol: [JUVE.MI]))
 - A.S. Roma S.P.A. (Stock Symbol: [ASR.MI]))
 - S.S. Lazio S.p.A. ([SSL.MI])

.The results data were then broken down according to the competition in which the result was achieved, the date, and what the result was. When combined with the stock data, preliminary analysis in python using plotly was carried out. Stock data was then split into two types of measurable short term change:

 - Change between matches: This was calculated as the close stock difference between the stock at close the next working day after a game vs the close stock of the next working day before the next game
 - Next working-day change: Change from close of the last working day before a game vs close of the next working day after a game

These two categories describe changes in stock game-game and immediate changes in stock and should therefore measure how much a given impact is likely to affect stock, giving an indication of how much these companies are financially impacted in the short term by their ability to achieve positive results. The first is more likely a better measurement of the impact of a given game, as not all the results of other teams have come in by the next working day after a match, and confidence may be less affected by prior negative or positive results, as they become more distant. 

&nbsp;
## Analyses performed

The following analyses were all performed over
Several factors were graphed for both seasons. The separately:

 - Result (Win, loss or draw) vs stock data over time
 - Table position vs stock data over time
 - Competition result vs stock data over time

Stock close data were grouped by season, competition and result, and game-game vs next-working day status. These groups, when sufficiently sized, were compared against each other and analyzed using the Kruskal-Wallis test, or, when available, the Kruskal-Wallis and either the Students T-Test or Welch T-Test. 

As there are many factors impacting a clubs stock over a season it was appropriate to use a non-parametric test to compare between groups. However, over a very short period of time it is not impossible that the stock of a club could fluctuate in a way according to normal distribution, if there is no change in this period in any other factors and results and table position are all consistent according to the expectations of investors. Because of this, after analysis according to the Shapiro test for normality, and the Levene test, it was considered that the Students T-Test, or Welch T-Test in some cases _may_ potentially provide more powerful analysis

&nbsp;
## Results


Graphing provided no obvious trends over time for any of the three clubs, though on the face of it it seemed that results in all competitions may have slightly impacted the stock value of lazio, and champions league results may have done the same for Juventus. Despite fairly consistent results and ranking, the stock value over time in both seasons was very different, which suggests a huge impact of external factors, e.g. merchandise, TV rights on stock price in the long-term.

Results of the Kruskal-Wallis and Students/Welch T-tests are provided. 


Juventus: 

 - Most likely, there is a very small difference in results in the 2017/18 season overall between games, with small positive impacts for wins and negative for losses and draws.
 - Results do not seem to make a difference in the 2018/19 season. 
 - Champions league results may impact stock differences in the later knockout rounds. 
 

Roma: 

 - Significant differences in stock valuation after results when all competitions were grouped together for the 2017/18 season
 - This was not the case when only domestic results were included, which perhaps indicates the champions league results were the main factor behind this.
 - Overall it is likely results did not impact stock price much either season


Lazio:

 -  This club has the strongest evidence for an impact of results on stock price. 
 -  It seems in most cases, a win and a loss will produce differentiable stock value changes over game-to-game and next-working-day timescales, though draws and losses, and draws and wins, are harder to differentiate
 -  The impact of results does not seem to change based on competition



&nbsp;
## Data sources

Stock data was sourced from https://finance.yahoo.com/ using the yfinance API [Node.js](https://nodejs.org/) v10+ to run.
Results were scraped from thttps://www.transfermarkt.co.uk/ using the requests library.






[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)


   [JUVE.MI]: <https://finance.yahoo.com/quote/juve.mi/>
   [ASR.MI]: <https://finance.yahoo.com/quote/asr.mi/>
   [SSL.MI]: <https://finance.yahoo.com/quote/SSL.MI/>
   
