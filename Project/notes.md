### Useful video ids:

##### HARRIS
_KCRsjPCiCI (Call Her Daddy)

##### TRUMP
qCbfTN-caFI (Lex Friedman)

---

### TODO:
* Add an SQLite Database to store the comments. It could maybe be just one comment table with a parent_id and video_id attribute.
* Mine data from the 2 videos above
* Extract the set of commentators from both videos and check how many commented under both (I am hoping between 200 and 1000)


https://www.fox9.com/news/which-podcasts-have-kamla-harris-donald-trump-done

* Il Sottografo con nodi aventi grado >= 2 è interessante.
* Il sottografo con nodi che hanno interagito in almeno due video è poco interessante: la maggior parte dei nodi è isolata.   
  E' poco interessante anche se applico il subgraph direttamente al primo sottografo.

------------------------

### RQ?:

“How does the structure and tone of engagement around tariff-related discussions differ across partisan platforms 
(Truth vs Bluesky), and what does this reveal about echo chamber formation?”

“How do partisan communities engage with each other on neutral platforms like YouTube, and what 
do those interactions reveal about conversational dynamics between political groups?”

------------------------

### What to do for the Analysis

Before starting the analysis these are the numbers I have:
- On Truth: 30k accounts and 75k posts
- On BlueSky: 15k accounts and 20k posts
- On Youtube: 18 videos (12 for trump, 6 for harris), 60k accounts and 115k comments


FOR Truth vs Bluesky:

- Consider Normalizing Networks by having two Networks with around same number of nodes (same order)
- Visualize the networks
- Basic measures:
  - Size and Order
  - Density
  - Average Degree
  - Connected Components
- Centralization and influence:
  - Degree Distribution (Centralization?)
  - Betweenness Centrality
  - Eigenvector Centrality
- Community Detection:
  - Modularity
  - Communities
- Activity Inequality:
  - Gini Coefficient on comments per user
  - Lorenz Curve
- Others:
  - Reciprocity
  - Link Strength
  - Stability: Social Balance Theory and Social Status Theory (after stance labels probably)
  - ECHO CHAMBERS 
- Then move on the semantic analysis...
  - Assortativity on those attributes...

What's not relevant:
- Clustering Coefficient (Transitivity)
- Average path length / diameter
- Assortativity (before stance labeling)

Questions: 
- Do I need to extract # of followers and following for each account?
- Should I extract the bio from the accounts? Could be significant to understand the stance / compare the stance
- Are the Social Media Platforms a good choice for this? Are they polarized? Can you measure that?

Use Echo Chamber Theory, Selective Exposure, or Deliberative Democracy theory as a frame.


FOR Youtube:

Notes:
- When users from opposing stances reply, do they reinforce, shift, or escalate?
- Are these discussions less likely to continue (shorter threads)?
- Does one side dominate the conversation?


In Part 2, lean on Conversational Breakdown literature or polarization through media research.

