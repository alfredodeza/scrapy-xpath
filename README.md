## Parsing With HTMLParser

Python has a built-in parser for HTML. Knowing how to use and take advantage of the HTMLParser library will help you when parsing is needed for simple tasks that do not need much effort.

This parser is simple to use but not very flexible if you need advanced support. The `HTMLParser` is a _streaming_ parser, which provides information about the parsing as it reads the document. This allows you to detect tags and data as it happens. It can get difficult to use when multiple nested tags that are similar exist, for example in a table with multiple rows.

Use the _scraping-with-htmlparser.ipynb_ file to use `HTMLParser` to extract data from HTML.

# Parsing with Scrapy and Xpath
Exercise for scraping using scrapy, parsing a real website, extracting key information that is not available through an API and using SQL to query it later. Again, you will use an already existing local HTML file that was previously downloaded and available in this repo. This prevents websites changing and breaking the parsing in this repository.

Objective: to extract the names and medal (or position) from the top three High Jumpers in the World Junior Championships as presented in their respective Wikipedia pages.

Install _requirements.txt_ in a virtual environment

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Note: You might get installation warnings about `PyDispatcher` or `Protego`. Ensure your installation works correctly by opening a Python prompt and importing the `scrapy` library. It should work without issues.

Get started with scrapy: https://docs.scrapy.org/en/latest/intro/tutorial.html


## Create a new project and a new spider

Scrapy has scaffolding that helps you get started with everything you need for a scraping project. Create a project and then a _spider_.

```
scrapy startproject wikipedia
scrapy genspider medalists wikipedia.org
```

Note that the name of the project and the spider must be different. Otherwise the spider will not get created.

## Use the scrapy shell

To help you building the scraping, use the scrapy shell (an interactive scraping shell) to work with the HTML files. The scrapy CLI allows you to use absolute paths. Go to the root of this repo and run the following to open up the local HTML file:

```
scrapy shell  "./html/1992_World_Junior_Championships_in_Athletics_–_Men's_high_jump"
```

Note that the quotes are required for the shell to work and escape the single quote within the HTML page. The shell uses a IPython as the shell (Jupyter-like output in the terminal) so be aware that when copying and pasting, you might need to reformat.

Confirm that the `response.url` points to the local path:

```
In [1]: response.url
Out[1]: 'file:///Users/alfredo/code/coursera/scraping-to-be-moved/html/1992_World_Junior_Championships_in_Athletics_%E2%80%93_Men%27s_high_jump'
```

Next, try to find the interesting table that holds the data we need. The target table has 3 items in it (first, second, and third place), so one way to find out if we have the right one is to check how many elements there are in each table.

```
In [18]: for table in response.xpath('//table'):
             print(table, len(table.xpath('tbody').xpath('tr')))

<Selector xpath='//table' data='<table class="sidebar-games-events si...'> 32
<Selector xpath='//table' data='<table class="wikitable" style="text-...'> 3
<Selector xpath='//table' data='<table class="wikitable sortable" sty...'> 20
<Selector xpath='//table' data='<table class="wikitable sortable" sty...'> 17
<Selector xpath='//table' data='<table class="wikitable sortable" sty...'> 17
<Selector xpath='//table' data='<table class="nowraplinks mw-collapsi...'> 3
```

That shows two potential tables that have the data we need. Use the first table (index position of `1`) that has three items in it and look within the `tr` tag:

```
In [24]: response.xpath('//table')[1].xpath('tbody').xpath('tr')
Out[24]:
[<Selector xpath='tr' data='<tr>\n<td bgcolor="gold"><b>Gold</b></...'>,
 <Selector xpath='tr' data='<tr>\n<td bgcolor="silver"><b>Silver</...'>,
 <Selector xpath='tr' data='<tr>\n<td bgcolor="CC9966"><b>Bronze</...'>]
```
That looks just right.

Make it easy to read and type by assigning the interesting table to a variable, and then try to find the "gold", "silver", and "bronze" values that will confirm the position of each athlete. These are in the `bgcolor` attribute of the `td` tag:

```
table = response.xpath('//table')[1].xpath('tbody')
In [69]: table.xpath('tr')
Out[69]:
[<Selector xpath='tr' data='<tr>\n<td bgcolor="gold"><b>Gold</b></...'>,
 <Selector xpath='tr' data='<tr>\n<td bgcolor="silver"><b>Silver</...'>,
 <Selector xpath='tr' data='<tr>\n<td bgcolor="CC9966"><b>Bronze</...'>]
 In [70]: table.xpath('tr')[0].xpath('td/@bgcolor').extract()
Out[70]: ['gold']
```

Now that the type of medal is known, look for the name of the athlete. The name is the value of the `a` tag. Use the `text()` helper in the Xpath selector:

```
In [74]: table.xpath('tr')[0].xpath('td/a/text()').extract()
Out[74]: ['Steve Smith']
```

Now put everything together to loop over the tables and extract the information:

```
In [75]: for tr in table.xpath('tr'):
             print(tr.xpath('td/@bgcolor').extract()[0],
             tr.xpath('td/a/text()').extract()[0]
             )

gold Steve Smith
silver Tim Forsyth
CC9966 Takahiro Kimino
```

That looks almost right. See the problem? What can you do to fix that `CC9966` value? The first thing to do is to inspect the html to see if there are any other indicatives of athlete placing:

```
In [76]: table.xpath('tr')[-1].xpath('td')
Out[76]:
[<Selector xpath='td' data='<td bgcolor="CC9966"><b>Bronze</b></td>'>,
 <Selector xpath='td' data='<td><a href="/wiki/Takahiro_Kimino" t...'>]
 ```

 So the `b` tag is showing "Bronze". Update the loop to use the value of the `b` tag instead of the `bgcolor` value:

 ```
 In [81]: for tr in table.xpath('tr'):
             print(tr.xpath('td/b/text()').extract()[0],
             tr.xpath('td/a/text()').extract()[0]
             )

Gold Steve Smith
Silver Tim Forsyth
Bronze Takahiro Kimino
```

## Efficiency

We've been using a pre-downloaded file available in this repo for the examples and notebook exercises. But, so far, I haven't explained _why_ this is a good idea or why you would want to try it out.

Usually, a spider will have a set of URLs that it will need to request when scraping. However, there are several problems with this approach when starting a scraping project to gather data. Let's go into some of the details regarding parsing live websites and requesting data each time.

### First iterations are always hard
In the current repo, I already solved how to get to the data. However, when you start working with a live website, you will have to take the time to find how to get to the data. Then, every time you "try it out" again, you need to make a live request to the website and download its contents.

This is not efficient, and it can be time-consuming. It also puts unnecessary strain on the webserver hosting the website. Being "nice" when parsing requires being aware that websites are resources that take money and effort to be available. Preventing an unnecessary burden to these websites is suitable for webservers and efficient for you since it is faster to read from a file. Every single time you need to start a `scrapy shell` again, it will be an order of magnitude faster.

### Testing
Websites change, and you might be getting some changes that are disruptive to your parsing. You can tweak the HTML and then use that tweaked file to run the spider against it by downloading the contents directly. This allows you to build a robust spider that can handle oddities on website content.
Changing HTML on the fly would be very difficult to get right instead of just changing the file directly.

### Speed
I've already mentioned that parsing a local file is an order of magnitude faster. There are always problems with scraping, like network errors, downtime on webservers, or even memory errors when parsing lots of data.
Imagine you have to parse several thousand pages and get into an unrecoverable error in the middle. It would be time-consuming to have to start from the very beginning.

### Updating the spider
If the requirements of the gathered data change, then you don't want to have to re-parse all those pages again. Of course, this depends if the data keeps changing. When updating the data requirements, you can use the same pages available on disk to do this.
