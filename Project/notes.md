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

Questions: 
- Do I need to extract # of followers and following for each account?
- Should I extract the bio from the accounts? Could be significant to understand the stance / compare the stance
- Are the Social Media Platforms a good choice for this? Are they polarized? Can you measure that?


FOR Truth vs Bluesky:

- Consider Normalizing Networks by having two Networks with around same number of nodes (same order)
- Visualize the networks
1. Basic measures:
  - Size and Order
  - Density
  - Average Degree
  - Connected Components
2. (ASK?) Centralization and influence:
  - Degree Distribution (Centralization?)
  - Betweenness Centrality
  - Eigenvector Centrality
3. Activity Inequality: > I USE THEM TO COMPARE THE DISTRIBUTIONS OF COMMENTS IN EACH NETWORK?
  CHECK OUT RANDOM NETWORK...
    - Gini Coefficient on comments per user
    - Lorenz Curve
4. Echo Chambers Theory (requires Machine Learning for content labeling)
ECHO CHAMBERS -> ECHO CHAMBERS THEORY:
   1. Network Modularity and Community Detection
   2. Stance Homogeneity within Communities (Check out Homophily from Echo Chambers paper)
   3. Stance Assortativity (SELECTIVE EXPOSURE)
   4. Information Diffusion Simulation (SIR Model - Check out part 2 from Echo Chambers paper)
5. (ASK?) Others:
  - Reciprocity
  - Link Strength
  - Stability: Social Balance Theory and Social Status Theory (after stance labels probably)


FOR Youtube:
-> IMPORTANT: Deliberative Democracy theory as a frame.

Notes:
- When users from opposing stances reply, do they reinforce, shift, or escalate?
- Are these discussions less likely to continue (shorter threads)?
- Does one side dominate the conversation?


In Part 2, lean on Conversational Breakdown literature or polarization through media research.

