### NetworkX Progress

##### 1. Quick View

This graph shows the essential intuition of drawing the NetworkX graph.

Just like this graph.

We have a table which contains the relationship between
a paper and its authors.

like:

`Paper1, authors: 1, 2, 3, 4`

`Paper2, authors: 2, 10, 11`

Within each paper's authors, we select two authors from them.
for paper1, the number of results is 2C4 = 4*3/2 = 6.

that is:
```
[1 2]
[1 3]
[2 3]
[2 4]
[3 4]
```
Paper2 shares the same story.


[a b] represent an edge (line segment) that connects two points a and b.

*Notice that a is smaller than b.*


* Graph

  ![net_tree](https://cloud.githubusercontent.com/assets/18824134/18615300/b9e9779a-7dd5-11e6-8cfb-fd889000b02b.jpg)

Basically, we will get a network from each paper.

However, if one author is an author of two papers, he can combine the two networks together.

Just as `author 2` does.


There is another way, that is transfer the network to the tree. Its mechanism is showed in the graph.

As a results, these two papers are separated.

__This is how networks work and what is the difference between Net and Tree.__

##### 2. Examples

1. A net example:

  ![screen shot 2016-09-18 at 3 12 36 pm](https://cloud.githubusercontent.com/assets/18824134/18615313/dcb9469c-7dd5-11e6-9979-4701967a8ede.png)

2. A tree example:

  ![screen shot 2016-09-18 at 3 12 46 pm](https://cloud.githubusercontent.com/assets/18824134/18615312/da32f6ac-7dd5-11e6-8df9-3e0f9495bfac.png)

3. The biggest net:

  ![screen shot 2016-09-16 at 6 20 41 pm](https://cloud.githubusercontent.com/assets/18824134/18615316/e5c806a6-7dd5-11e6-8708-0bb205287fa3.png)

4. The biggest tree:

  ![largestcommunity](https://cloud.githubusercontent.com/assets/18824134/18615335/9b26c83e-7dd6-11e6-85d0-b5082b53bcf1.png)

##### 3. Further issues

We can certainly change the style of the graph.

Here is an example:

__The nodes are assigned with some weight values before!__

We can modify the edges, nodes and labels with some assigned weights.

* Graph

  ![screen shot 2016-09-18 at 3 14 28 pm](https://cloud.githubusercontent.com/assets/18824134/18615309/d637f458-7dd5-11e6-9f3b-1941b27d35af.png)


1. Problem one:

  Add what attribute vectors to the nodes and edges, and represnet them with what colors, line styles and etc.

2. Problem two:

  How to select a good position distribution for these nodes in order to contain some information.

3. Problem three:

  How to make these graphs (or subgraphs) dynamic and interactive by `plotly` or `mayavi`?
